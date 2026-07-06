import sqlite3
from datetime import datetime, date
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).resolve().parent / "data" / "procesos.db"


def try_parse_fecha(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
DB_PATH.parent.mkdir(exist_ok=True)

AREAS = [
    "CLASIFICADO ENTERO",
    "CLASIFICADO COLA",
    "DESCABEZADO",
    "DESCONGELADO",
    "EMPAQUE",
    "MASTERIZADO",
    "PELADO",
    "TRATAMIENTO",
    "TUNEL IQF",
    "REEMPAQUE",
    "REETIQUETADO",
]

NO_APLICA_AREAS = {"CLASIFICADO COLA", "PELADO", "DESCABEZADO", "TRATAMIENTO", "DESCONGELADO"}
NO_PRESENTACION_AREAS = {"CLASIFICADO COLA", "PELADO", "DESCABEZADO", "TRATAMIENTO"}

PRODUCTOS = [
    "GRANEL",
    "DESCOMPUESTO",
    "BASURA",
    "DESCABEZADO",
    "ENTERO",
    "ENTERO-SIFON",
    "ENTERO-IQF",
    "ENTERO-R",
    "ENTERO 100% MUDADO",
    "COLA",
    "COLA-SIFON",
    "COLA-IQF",
    "COLA-R",
    "P&D T-ON",
    "P&D T-OFF",
    "P&D T-OFF CC",
    "P&D T-OFF R",
    "PPV T-ON",
    "PPV T-OFF",
    "PPV T-OFF CC",
    "PUD T-ON",
    "PUD T-OFF",
    "PUD T-OFF R",
    "PUD T-OFF CC",
    "BF T-ON",
    "BF T-OFF",
    "BF T-OFF R",
    "BF T-ON ALINEADO",
    "3/4 T-ON",
    "3/4 T-OFF",
    "3/4 T-ON CC",
    "BUTTER ROUND PyD T-ON",
    "PINCHOS T-ON",
    "PINCHOS T-OFF",
    "PINCHOS BF",
    "PINCHOS BF ENTERO",
    "ENTERO BF",
    "COCINADO ENTERO",
    "COCINADO COLA",
    "COCINADO EZ-PEEL",
    "COCINADO P&D T-ON",
    "COCINADO P&D T-OFF",
    "COCINADO P&D T-OFF CC",
    "COCINADO PPV T-ON",
    "COCINADO PPV T-OFF",
    "COCINADO PPV T-OFF CC",
    "COCINADO PUD T-ON",
    "COCINADO PUD T-OFF",
    "COCINADO PUD T-OFF CC",
    "EMPANIZADO P&D T-ON",
    "EMPANIZADO P&D T-OFF",
    "EMPANIZADO PPV T-ON",
    "EMPANIZADO PPV T-OFF",
    "EMPANIZADO PUD T-ON",
    "EMPANIZADO PUD T-OFF",
    "EMPANIZADO BF T-ON",
    "PPV T-OFF R",
    "SP-CASCARA",
    "SP-CASCARA Y CABEZA",
]

CLIENTES = [
    "OROPSA",
    "OFICINAS CENTRALES",
    "PRODUCTO PARA PELADO",
    "YENS",
    "LEQUALITY",
    "I OCEAN",
    "PESCADORES",
    "GOLD LAKE",
    "GOLD LAKE BELLA",
    "UNION MARINE",
    "RED CHAMBER COMPANY",
    "PESCANOVA USA",
    "INDUPECASA",
    "WALMART",
    "SUMINISTROS",
    "UNISUPER",
    "VENTA LOCAL",
    "SIN CLIENTE",
    "LAI LAI",
    "RINOLI S.A",
    "(pendiente de definir)",
    "IMPORTADORA Y EXPORTADORA DE MARISCOS DE CENTRO AMERICA Y EL CARIBE S.A DE CV",
    "EL HUEVO FRITO S.A.",
    "OCEANA",
]

TALLAS = [
    "6 OZ",
    "4 OZ",
    "8 OZ",
    "L1",
    "L2",
    "L1 11/20",
    "U/10",
    "U/15",
    "10/20",
    "U/8",
    "21/25",
    "20/30",
    "31/35",
    "30/40",
    "40/50",
    "50/60",
    "60/70",
    "70/80",
    "80/100",
    "90/100",
    "100/120",
    "120/150",
    "150/200",
    "200/300",
    "300/400",
    "33/37",
    "C1 30/55",
    "ROTA",
    "56/100",
    "MIX",
    "U/15",
    "C1",
    "C2",
    "16/20",
    "21/25",
    "21/30",
    "26/30",
    "31/35",
    "31/40",
    "36/40",
    "41/50",
    "51/60",
    "61/70",
    "80/120",
    "71/90",
    "91/110",
    "91/120",
    "110/130",
    "130/150",
    "150/200",
    "200/300",
    "1 GRAMOS",
    "2 GRAMOS",
    "3 GRAMOS",
    "4 GRAMOS",
    "5 GRAMOS",
    "6 GRAMOS",
    "7 GRAMOS",
    "8 GRAMOS",
    "9 GRAMOS",
    "10 GRAMOS",
    "11 GRAMOS",
    "12 GRAMOS",
    "13 GRAMOS",
    "14 GRAMOS",
    "15 GRAMOS",
    "16 GRAMOS",
    "17 GRAMOS",
    "18 GRAMOS",
    "19 GRAMOS",
    "20 GRAMOS",
    "21 GRAMOS",
    "22 GRAMOS",
    "23 GRAMOS",
    "24 GRAMOS",
    "25 GRAMOS",
    "26 GRAMOS",
    "27 GRAMOS",
    "28 GRAMOS",
    "29 GRAMOS",
    "30 GRAMOS",
    "31 GRAMOS",
    "32 GRAMOS",
    "33 GRAMOS",
    "34 GRAMOS",
    "35 GRAMOS",
    "36 GRAMOS",
    "37 GRAMOS",
    "38 GRAMOS",
    "39 GRAMOS",
    "40 GRAMOS",
    "41 GRAMOS",
    "42 GRAMOS",
    "43 GRAMOS",
    "44 GRAMOS",
    "45 GRAMOS",
    "46 GRAMOS",
    "47 GRAMOS",
    "48 GRAMOS",
    "49 GRAMOS",
    "50 GRAMOS",
    "51 GRAMOS",
    "52 GRAMOS",
    "53 GRAMOS",
    "54 GRAMOS",
    "55 GRAMOS",
    "56 GRAMOS",
    "57 GRAMOS",
    "58 GRAMOS",
    "59 GRAMOS",
    "60 GRAMOS",
    "66 GRAMOS",
    "SIN TALLA",
    "BROKEN",
    "SMALL BROKEN",
    "MEDIUM BROKEN",
    "BIG BROKEN",
    "PEQUEÑO (60/70 - 150/200)",
    "MEDIANO (30/40 - 50/60)",
    "GRANDE",
]

PRESENTACIONES = [
    "1/1 kg (1 kg)",
    "2/10 kg (20 kg)",
    "10/3 lb (30 lb)",
    "7/4 lb (28 lb)",
    "19/1.18 lb (22..42 lb)",
    "20/0.5 lb(10lb)",
    "32/4-6 oz (10lb)",
    "40/4 oz (10 lb)",
    "26/6 oz (10 lb)",
    "20/8 oz (10 lb)",
    "16/10 oz (10 lb)",
    "40/ 8 oz(20 lb)",
    "1/10 (10 kg)",
    "10/1-3 oz (10 lb)",
    "5/4 lb (20 lb)",
    "3/6 kg (18 kg)",
    "30/1 lb (30 lb)",
    "7/2 KG",
    "19/1.05 lb (20 lb)",
    "24/450 gr (10.89 kg)",
    "18/1.11 lb (20 lb)",
    "12/450 gr (5.4 kg)",
    "24/450 gr (10.8 kg)",
    "16/450 gr (7.2 kg)",
    "22/450 gr (9.9 kg)",
    "20/450 gr(9 kg)",
    "12/480 gr(5.76kg)",
    "16/480 gr (7.68 kg)",
    "24/454 gr (10.89 kg)",
    "22/480 gr (10.56 kg)",
    "12/600 gr(7.2 kg)",
    "14/650 gr (9.1 kg)",
    "14/0.454 kg (6.35 kg)",
    "22/650 gr (14.3 kg)",
    "12/650 gr (7.7 kg)",
    "22/680 gr (14.96 kg)",
    "24/600 gr(14.4 kg)",
    "16/650 gr (10.4 kg)",
    "20/650 gr (13 kg)",
    "14/680 gr (9.52 kg)",
    "19/523 gr (9.9 kg)",
    "10/ 720 gr (7.2 kg)",
    "5/2 kg(10kg)",
    "10/1 lb (10 lb)",
    "5/2 lb (10 lb)",
    "4/5 lb (20 lb)",
    "1/15 lb (15 lb)",
    "25/1 lb (25 lb)",
    "6/3 lb (18 lb)",
    "9/2 lb (18 lb)",
    "10/2 lb (20 lb)",
    "4/3 lb (12 lb)",
    "20/1 lb (20 lb)",
    "20/340 gr (6.8 kg)",
    "14/1.5 lb (21 lb)",
    "6/4 lb (24 lb)",
    "6/4.4 lb (26.4 lb)",
    "14/2 lb (28 lb)",
    "1/30 lb (30 lb)",
    "10/4 lb (40 lb)",
    "1/20 lb (20 lb)",
    "2/20 lb (40 lb)",
    "1/25 lb (25lb)",
    "1/40 lb (40 lb)",
    "10/5 lb (50 lb)",
    "10/4 lb (40 lb)",
    "1/50 lb (50 lb)",
    "24/1 lb (24 lb)",
    "10/720 gr(7.2 kg)",
    "12/1 LB (12 lb)",
    "19/500 gr (9.5kg)",
    "20/375 gr (7.5 kg)",
    "14/700 gr (9.8kg)",
    "20/360 gr(7.2 kg)",
    "1/10 lb (10 lb)",
    "25/360 gr (9 kg)",
    "10/2 kg (20 kg)",
    "20/420 gr (8.4 kg)",
    "10/908 gr (9.08 kg)",
    "6/2 kg (12 kg)",
    "8/2 kg (16 kg)",
    "14/3 lb (42 lb)",
    "4/2 Kg (8 Kg)",
    "6/5 lb (30 lb)",
    "8/5 lb (40 lb)",
    "6/1 lb (6 lb)",
    "6/2 lb (12 lb)",
    "8/4 lb (32 lb)",
]

# Lista de piscinas proporcionada por el usuario
POOLS = [
    "TM01-E01","TM01-E02","TM01-E03","TM01-E04","TM01-P01","TM01-P02","TM01-P03","TM00-P0A",
    "TM02-E01","TM02-E02","TM02-E03","TM02-E04","TM02-E05","TM02-P01","TM02-P02","TM02-P03","TM02-P04",
    "TM03-E01","TM03-E02","TM03-E03","TM03-E04","TM03-P01",
    "TM04-E01","TM04-E02","TM04-E03","TM04-E04","TM04-E05","TM04-E06","TM04-E07",
    "TM05-E01","TM05-E02","TM05-E03","TM05-E04","TM05-E05","TM05-E06","TM05-P01","TM05-P02","TM05-P03",
    "TM06-E01","TM06-E02","TM06-E03","TM06-E04","TM06-E05","TM06-E06",
    "EM00-PC1","EM00-PC2","EM00-PC3","EM00-PC4",
    "EM01-E01","EM01-E02","EM01-E03","EM01-E04",
    "EM02-E01","EM02-E02","EM02-E03","EM02-E04","EM02-E05",
    "EM03-E01","EM03-E02","EM03-E03","EM03-E04","EM03-E05","EM03-P01","EM03-P02","EM03-P03","EM03-P04",
    "EM04-E01","EM04-E02","EM04-E03","EM04-E04","EM04-E05","EM04-E06","EM04-E07","EM04-E08","EM04-P01","EM04-P02","EM04-P03","EM04-P04",
    "EM05-E01","EM05-E02","EM05-E03","EM05-E04","EM05-E05","EM05-E06","EM05-P01","EM05-P02","EM05-P03",
    "EM06-E01","EM06-E02","EM06-E03","EM06-E04","EM06-E05","EM06-E06",
]

# Ciclos del 1 al 30 como strings para el selectbox
CICLOS = [str(i) for i in range(1, 31)]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='registros'"
        ).fetchone()

        if table_exists is None:
            conn.execute(
                """
                CREATE TABLE registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    turno TEXT NOT NULL,
                    area TEXT NOT NULL,
                    tipo_producto TEXT,
                    lote TEXT,
                    lote_codigo TEXT,
                    piscina TEXT,
                    ciclo INTEGER,
                    cliente TEXT,
                    tallas TEXT,
                    presentacion TEXT,
                    kg_recibidos REAL,
                    kg_procesados REAL,
                    rendimiento REAL,
                    no_personas INTEGER,
                    observaciones TEXT,
                    creado_en TEXT NOT NULL
                )
                """
            )
            conn.commit()
            return

        cols = [row["name"] for row in conn.execute("PRAGMA table_info(registros)").fetchall()]
        if "valor" in cols or "unidad" in cols:
            conn.execute("ALTER TABLE registros RENAME TO registros_legacy")
            conn.execute(
                """
                CREATE TABLE registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    turno TEXT NOT NULL,
                    area TEXT NOT NULL,
                    tipo_producto TEXT,
                    lote TEXT,
                    cliente TEXT,
                    tallas TEXT,
                    presentacion TEXT,
                    kg_recibidos REAL,
                    kg_procesados REAL,
                    rendimiento REAL,
                    no_personas INTEGER,
                    observaciones TEXT,
                    creado_en TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO registros (
                    id, fecha, turno, area, tipo_producto, lote, cliente, tallas, presentacion,
                    kg_recibidos, kg_procesados, rendimiento, no_personas, observaciones, creado_en
                )
                SELECT
                    id,
                    fecha,
                    turno,
                    area,
                    COALESCE(tipo_producto, ''),
                    COALESCE(lote, ''),
                    COALESCE(cliente, ''),
                    COALESCE(tallas, ''),
                    COALESCE(presentacion, 'No aplica'),
                    COALESCE(kg_recibidos, 0),
                    COALESCE(kg_procesados, 0),
                    COALESCE(rendimiento, 0),
                    COALESCE(no_personas, 0),
                    COALESCE(observaciones, ''),
                    COALESCE(creado_en, datetime('now'))
                FROM registros_legacy
                """
            )
            conn.execute("DROP TABLE registros_legacy")
            conn.commit()
            cols = [row["name"] for row in conn.execute("PRAGMA table_info(registros)").fetchall()]

        for col, col_type in {
            "tipo_producto": "TEXT",
            "lote": "TEXT",
            "lote_codigo": "TEXT",
            "piscina": "TEXT",
            "ciclo": "INTEGER",
            "cliente": "TEXT",
            "tallas": "TEXT",
            "presentacion": "TEXT",
            "kg_recibidos": "REAL",
            "kg_procesados": "REAL",
            "rendimiento": "REAL",
            "no_personas": "INTEGER",
            "observaciones": "TEXT",
        }.items():
            if col not in cols:
                conn.execute(f"ALTER TABLE registros ADD COLUMN {col} {col_type}")
        conn.commit()


def get_registros(area_filter="Todas"):
    with get_connection() as conn:
        if area_filter and area_filter != "Todas":
            rows = conn.execute(
                """
                  SELECT id, fecha, turno, area, tipo_producto, lote, lote_codigo, piscina, ciclo, cliente, tallas, presentacion,
                      kg_recibidos, kg_procesados, rendimiento, no_personas, observaciones, creado_en
                FROM registros
                WHERE area = ?
                ORDER BY fecha DESC, id DESC
                """,
                (area_filter,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                  SELECT id, fecha, turno, area, tipo_producto, lote, lote_codigo, piscina, ciclo, cliente, tallas, presentacion,
                      kg_recibidos, kg_procesados, rendimiento, no_personas, observaciones, creado_en
                FROM registros
                ORDER BY fecha DESC, id DESC
                """
            ).fetchall()
    return [dict(row) for row in rows]


def insertar_registro(fecha, turno, area, tipo_producto, lote, lote_codigo, piscina, ciclo, cliente, tallas, presentacion, kg_recibidos, kg_procesados, rendimiento, no_personas, observaciones):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO registros (
                fecha, turno, area, tipo_producto, lote, lote_codigo, piscina, ciclo, cliente, tallas, presentacion,
                kg_recibidos, kg_procesados, rendimiento, no_personas, observaciones, creado_en
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fecha,
                turno,
                area,
                tipo_producto,
                lote,
                lote_codigo,
                piscina,
                ciclo,
                cliente,
                tallas,
                presentacion,
                kg_recibidos,
                kg_procesados,
                rendimiento,
                no_personas,
                observaciones,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()


def actualizar_registro(registro_id, fecha, turno, area, tipo_producto, lote, lote_codigo, piscina, ciclo, cliente, tallas, presentacion, kg_recibidos, kg_procesados, rendimiento, no_personas, observaciones):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE registros
            SET fecha = ?, turno = ?, area = ?, tipo_producto = ?, lote = ?, lote_codigo = ?, piscina = ?, ciclo = ?, cliente = ?, tallas = ?, presentacion = ?,
                kg_recibidos = ?, kg_procesados = ?, rendimiento = ?, no_personas = ?, observaciones = ?
            WHERE id = ?
            """,
            (
                fecha,
                turno,
                area,
                tipo_producto,
                lote,
                lote_codigo,
                piscina,
                ciclo,
                cliente,
                tallas,
                presentacion,
                kg_recibidos,
                kg_procesados,
                rendimiento,
                no_personas,
                observaciones,
                registro_id,
            ),
        )
        conn.commit()


def eliminar_registro(registro_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM registros WHERE id = ?", (registro_id,))
        conn.commit()


st.set_page_config(page_title="Control de planta de camarón", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #b8d0eb; }
    [data-testid="stImage"] > img { background: transparent !important; }
    </style>
""", unsafe_allow_html=True)

_col_title, _col_logo = st.columns([3, 1])
with _col_title:
    st.title("Planta de Proceso OROPSA")
    st.markdown("<p style='font-size:20px;'>Sistema de manejo de información en planta procesadora.</p>", unsafe_allow_html=True)
with _col_logo:
    st.image("LogoV2-removebg-preview.png", use_container_width=True)

init_db()

with st.sidebar:
    st.header("Áreas")
    selected_area = st.selectbox("Selecciona el área", AREAS, index=0)
    st.caption("Elige el área desde la lista para registrar la producción.")
    st.divider()
    area_filter = st.selectbox("Filtrar historial", ["Todas", *AREAS])

registros = get_registros(area_filter)

if registros:
    df = pd.DataFrame(registros)
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d")
    total_recibidos = df["kg_recibidos"].fillna(0).sum()
    total_procesados = df["kg_procesados"].fillna(0).sum()
else:
    df = pd.DataFrame(columns=["id", "fecha", "turno", "area", "tipo_producto", "lote", "lote_codigo", "piscina", "ciclo", "cliente", "tallas", "presentacion", "kg_recibidos", "kg_procesados", "rendimiento", "no_personas", "observaciones", "creado_en"])
    total_recibidos = 0
    total_procesados = 0

st.subheader("Resumen")
col1, col2, col3 = st.columns(3)
col1.metric("Registros", len(registros))
col2.metric("Área seleccionada", selected_area)
col3.metric("KG procesados", f"{total_procesados:,.0f}")

st.divider()

with st.container(border=True):
    st.subheader(f"Captura de {selected_area}")

    # Código, Piscina y Ciclo fuera del form para lote en tiempo real
    _ca, _ = st.columns(2)
    with _ca:
        codigo = st.text_input("Código", key="frm_codigo", placeholder="Ej. G326")
        if POOLS:
            _sel_piscina = st.selectbox("Piscina", ["Selecciona", *POOLS], key="frm_piscina")
            piscina = _sel_piscina if _sel_piscina != "Selecciona" else ""
        else:
            piscina = st.text_input("Piscina", key="frm_piscina_manual", placeholder="(lista no cargada)")
        _sel_ciclo = st.selectbox("Ciclo", ["Selecciona", *CICLOS], key="frm_ciclo")
        ciclo = int(_sel_ciclo) if _sel_ciclo not in ("Selecciona", "") and _sel_ciclo else None
        _parts = []
        if codigo: _parts.append(codigo)
        if piscina: _parts.append(piscina)
        if ciclo: _parts.append(str(ciclo))
        lote = "-".join(_parts)
        st.text_input("Lote unificado", value=lote, disabled=True)

    with st.form("nuevo_registro", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            fecha_text = st.text_input("Fecha", value=date.today().strftime("%d/%m/%Y"), placeholder="dd/mm/aaaa")
            fecha_obj = try_parse_fecha(fecha_text)
            turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche", "Otro"])
            tipo_producto = st.selectbox("Tipo de producto", ["Selecciona", *PRODUCTOS])
            if selected_area in NO_APLICA_AREAS:
                cliente = "No aplica"
                st.text_input("Cliente", value=cliente, disabled=True)
            else:
                cliente = st.selectbox("Cliente", ["Selecciona", *CLIENTES])
        with col_b:
            seleccion_talla = st.selectbox("Tallas", ["Selecciona", *TALLAS])
            tallas = seleccion_talla if seleccion_talla != "Selecciona" else ""
            if selected_area in NO_PRESENTACION_AREAS:
                presentacion = "No aplica"
                st.text_input("Presentación", value=presentacion, disabled=True)
            else:
                seleccion_presentacion = st.selectbox("Presentación", ["Selecciona", *PRESENTACIONES])
                presentacion = seleccion_presentacion if seleccion_presentacion != "Selecciona" else ""
            kg_recibidos = st.number_input("KG recibidos", min_value=0.0, step=1.0)
            kg_procesados = st.number_input("KG procesados", min_value=0.0, step=1.0)
            no_personas = st.number_input("No. personas", min_value=0, step=1, format="%d")

        rendimiento_calculado = 0.0
        if kg_recibidos > 0:
            rendimiento_calculado = round((kg_procesados / kg_recibidos) * 100, 2)

        st.markdown(f"**Rendimiento calculado: {rendimiento_calculado:.2f}%**")
        observaciones = st.text_area("Observaciones")

        submitted = st.form_submit_button("Guardar registro")
        if submitted:
            if fecha_obj is None:
                st.error("Ingresa la fecha en formato dd/mm/aaaa.")
            else:
                presentacion_value = (presentacion or "").strip()
                if not presentacion_value:
                    presentacion_value = "No aplica"
                insertar_registro(
                    fecha_obj.strftime("%Y-%m-%d"),
                    turno,
                    selected_area,
                    tipo_producto,
                    lote,
                    codigo,
                    piscina,
                    ciclo,
                    cliente,
                    tallas,
                    presentacion_value,
                    float(kg_recibidos),
                    float(kg_procesados),
                    float(rendimiento_calculado),
                    int(no_personas),
                    observaciones,
                )
            for _k in ("frm_codigo", "frm_piscina", "frm_piscina_manual", "frm_ciclo"):
                st.session_state.pop(_k, None)
            st.success("Registro guardado")
            st.rerun()

st.divider()

st.subheader("Editar o eliminar registros")
if registros:
    registros_por_id = {registro["id"]: registro for registro in registros}
    selected_id = st.selectbox(
        "Selecciona un registro para editar o eliminar",
        options=list(registros_por_id.keys()),
        format_func=lambda id_: f"#{id_} - {registros_por_id[id_]['fecha']} | {registros_por_id[id_]['area']}",
    )
    registro = registros_por_id[selected_id]

    with st.form("editar_registro"):
        col_x, col_y = st.columns(2)
        with col_x:
            edit_fecha_text = st.text_input(
                "Fecha",
                value=datetime.strptime(registro["fecha"], "%Y-%m-%d").date().strftime("%d/%m/%Y"),
                placeholder="dd/mm/aaaa",
            )
            edit_fecha_obj = try_parse_fecha(edit_fecha_text)
            edit_turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche", "Otro"], index=["Mañana", "Tarde", "Noche", "Otro"].index(registro["turno"]))
            edit_area = st.selectbox("Área", AREAS, index=AREAS.index(registro["area"]))
            edit_tipo_producto = st.selectbox(
                "Tipo de producto",
                ["Selecciona", *PRODUCTOS],
                index=PRODUCTOS.index(registro["tipo_producto"]) + 1 if registro["tipo_producto"] in PRODUCTOS else 0,
            )
            # Código (parte inicial del lote)
            edit_codigo = st.text_input("Código", value=registro.get("lote_codigo") or registro.get("lote") or "")
            edit_lote = edit_codigo
            # Piscina
            if POOLS:
                edit_seleccion_piscina = st.selectbox(
                    "Piscina",
                    ["Selecciona", *POOLS],
                    index=POOLS.index(registro.get("piscina")) + 1 if registro.get("piscina") in POOLS else 0,
                )
                edit_piscina = edit_seleccion_piscina if edit_seleccion_piscina != "Selecciona" else ""
            else:
                edit_piscina = st.text_input("Piscina", value=registro.get("piscina") or "")

            # Ciclo
            edit_seleccion_ciclo = st.selectbox(
                "Ciclo",
                ["Selecciona", *CICLOS],
                index=CICLOS.index(str(registro.get("ciclo"))) + 1 if registro.get("ciclo") else 0,
            )
            edit_ciclo = int(edit_seleccion_ciclo) if edit_seleccion_ciclo != "Selecciona" and edit_seleccion_ciclo else None

            # Generar lote unificado para edición
            edit_parts = []
            if edit_codigo:
                edit_parts.append(edit_codigo)
            if edit_piscina:
                edit_parts.append(edit_piscina)
            if edit_ciclo:
                edit_parts.append(str(edit_ciclo))
            edit_lote = "-".join(edit_parts)
            st.text_input("Lote unificado", value=edit_lote, disabled=True)
            if edit_area in NO_APLICA_AREAS:
                edit_cliente = "No aplica"
                st.text_input("Cliente", value=edit_cliente, disabled=True)
            else:
                edit_cliente = st.selectbox(
                    "Cliente",
                    ["Selecciona", *CLIENTES],
                    index=CLIENTES.index(registro["cliente"]) + 1 if registro["cliente"] in CLIENTES else 0,
                )
        with col_y:
            edit_seleccion_talla = st.selectbox(
                "Tallas",
                ["Selecciona", *TALLAS],
                index=TALLAS.index(registro["tallas"]) + 1 if registro["tallas"] in TALLAS else 0,
            )
            edit_tallas = edit_seleccion_talla if edit_seleccion_talla != "Selecciona" else ""

            if edit_area in NO_PRESENTACION_AREAS:
                edit_presentacion = "No aplica"
                st.text_input("Presentación", value=edit_presentacion, disabled=True)
            else:
                edit_seleccion_presentacion = st.selectbox(
                    "Presentación",
                    ["Selecciona", *PRESENTACIONES],
                    index=PRESENTACIONES.index(registro["presentacion"]) + 1 if registro["presentacion"] in PRESENTACIONES else 0,
                )
                edit_presentacion = edit_seleccion_presentacion if edit_seleccion_presentacion != "Selecciona" else ""

            edit_kg_recibidos = st.number_input("KG recibidos", min_value=0.0, step=1.0, value=float(registro["kg_recibidos"] or 0))
            edit_kg_procesados = st.number_input("KG procesados", min_value=0.0, step=1.0, value=float(registro["kg_procesados"] or 0))
            edit_rendimiento = st.number_input("Rendimiento (%)", min_value=0.0, max_value=100.0, step=0.1, value=float(registro["rendimiento"] or 0))
            edit_no_personas = st.number_input("No. personas", min_value=0, step=1, format="%d", value=int(registro["no_personas"] or 0))
        edit_observaciones = st.text_area("Observaciones", value=registro["observaciones"] or "")

        btn_update = st.form_submit_button("Actualizar")
        if btn_update:
            if edit_fecha_obj is None:
                st.error("Ingresa la fecha en formato dd/mm/aaaa.")
            else:
                edit_presentacion_value = (edit_presentacion or "").strip()
                if not edit_presentacion_value:
                    edit_presentacion_value = "No aplica"
                actualizar_registro(
                    selected_id,
                    edit_fecha_obj.strftime("%Y-%m-%d"),
                    edit_turno,
                    edit_area,
                    edit_tipo_producto,
                    edit_lote,
                    edit_codigo,
                    edit_piscina,
                    edit_ciclo,
                    edit_cliente,
                    edit_tallas,
                    edit_presentacion_value,
                    float(edit_kg_recibidos),
                    float(edit_kg_procesados),
                    float(edit_rendimiento),
                    int(edit_no_personas),
                    edit_observaciones,
                )
                st.success("Registro actualizado")
                st.rerun()

    if st.button("Eliminar registro seleccionado"):
        eliminar_registro(selected_id)
        st.success("Registro eliminado")
        st.rerun()
else:
    st.info("Aún no hay registros para editar o eliminar.")

st.divider()

st.subheader("Historial")
if not df.empty:
    display_df = df[["id", "fecha", "turno", "area", "tipo_producto", "lote", "lote_codigo", "piscina", "ciclo", "cliente", "tallas", "presentacion", "kg_recibidos", "kg_procesados", "rendimiento", "no_personas", "observaciones", "creado_en"]].copy()
    st.table(display_df)

    excel_buffer = BytesIO()
    display_df.to_excel(excel_buffer, index=False, sheet_name="Registros")
    excel_bytes = excel_buffer.getvalue()
    st.download_button(
        label="Descargar Excel",
        data=excel_bytes,
        file_name="registros_planta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("No hay datos para mostrar todavía.")
