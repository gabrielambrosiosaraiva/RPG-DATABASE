import os
import streamlit as st
import oracledb
import pandas as pd

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_DSN = os.environ.get("DB_DSN")

def get_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

def listar_herois():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome, classe, hp_atual, hp_max, status FROM TB_HEROIS")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return dados

def processar_turno():
    conn = get_connection()
    cur = conn.cursor()
    plsql = """
        DECLARE
            v_dano NUMBER := 10;
            v_hp NUMBER;
        BEGIN
            FOR r IN (SELECT id_heroi, hp_atual FROM TB_HEROIS WHERE status = 'ATIVO') LOOP
                v_hp := r.hp_atual - v_dano;
                IF v_hp <= 0 THEN
                    UPDATE TB_HEROIS
                    SET hp_atual = 0,
                        status = 'CAÍDO'
                    WHERE id_heroi = r.id_heroi;
                ELSE
                    UPDATE TB_HEROIS
                    SET hp_atual = v_hp
                    WHERE id_heroi = r.id_heroi;
                END IF;
            END LOOP;
            COMMIT;
        END;
    """
    cur.execute(plsql)
    cur.close()
    conn.close()

def restaurar_herois():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM TB_HEROIS WHERE status = 'CAÍDO'")
    qtd = cur.fetchone()[0]
    if qtd == 0:
        msg = "Somente heróis caídos podem receber a Bênção de Galadriel."
    else:
        plsql = """
        BEGIN
            UPDATE TB_HEROIS
            SET hp_atual = hp_max,
                status = 'ATIVO'
            WHERE status = 'CAÍDO';
            COMMIT;
        END;
        """
        cur.execute(plsql)
        msg = "Vida dos heróis caídos restaurada ao máximo!"
    cur.close()
    conn.close()
    return msg


def colorir_status(val):
    if val == "CAÍDO":
        return "background-color: #ff4d4d; color: black; font-weight: bold; text-align: center;"
    elif val == "ATIVO":
        return "background-color: #33cc33; color: black; font-weight: bold; text-align: center;"
    return "text-align: center;"

st.title("SQLgard O Despertar do Kernel Ancestral e Os Anéis do Poder")

col1, col2 = st.columns(2)

with col1:
    if st.button("Próximo Turno"):
        processar_turno()
        st.success("Turno processado!")

with col2:
    if st.button("Aplicar Bênção de Galadriel"):
        msg = restaurar_herois()
        if "Somente" in msg:
            st.warning(msg)
        else:
            st.success(msg)

herois = listar_herois()
df = pd.DataFrame(herois, columns=["Nome", "Classe", "HP Atual", "HP Máx", "Status"])

df_styled = df.style.applymap(colorir_status, subset=["Status"])
st.subheader("Estado dos Heróis")
st.dataframe(df_styled)


st.markdown(
    """
    <div style="background-color:#222; padding:15px; border-radius:10px; color:white; text-align:center;">
        <b>A Névoa Ancestral</b> envolve o campo de batalha.<br>
        Cada turno, ela drena <span style="color:red; font-weight:bold;">10 pontos de HP</span> dos heróis ativos.
    </div>
    """,
    unsafe_allow_html=True
)