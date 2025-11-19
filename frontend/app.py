import streamlit as st
import requests
import os
import json

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="AI Claims Processing", layout="wide")

def upload_page():
    st.header("Nahlásenie poistnej udalosti")
    st.write("Nahrajte dokumenty k vašej poistnej udalosti (PDF).")
    
    uploaded_files = st.file_uploader("Vyberte súbory", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Odoslať"):
            with st.spinner("Nahrávam súbory..."):
                try:
                    files = [("files", (file.name, file, file.type)) for file in uploaded_files]
                    response = requests.post(f"{BACKEND_URL}/upload/", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Súbory úspešne nahrané! Vytvorený nárok ID: {data['id']}")
                        st.info("Váš nárok sa spracováva. Prosím čakajte na vyjadrenie.")
                    else:
                        st.error(f"Chyba pri nahrávaní: {response.text}")
                except Exception as e:
                    st.error(f"Nepodarilo sa pripojiť k serveru: {e}")

def admin_dashboard():
    st.header("Admin Dashboard - Likvidácia")
    
    # Fetch claims
    try:
        response = requests.get(f"{BACKEND_URL}/claims/")
        if response.status_code == 200:
            claims = response.json()
        else:
            st.error("Nepodarilo sa načítať zoznam claimov.")
            claims = []
    except Exception as e:
        st.error(f"Chyba pripojenia: {e}")
        claims = []
        
    if not claims:
        st.info("Žiadne claimy na zobrazenie.")
        return

    # List view
    for claim in claims:
        with st.expander(f"Claim #{claim['id']} - {claim['status']}"):
            st.write(f"Vytvorené: {claim['created_at']}")
            
            # Display Documents
            st.subheader("Dokumenty")
            if 'documents' in claim:
                for doc in claim['documents']:
                    st.markdown(f"**{doc['filename']}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Pôvodný text")
                        st.text_area("Original", doc.get('original_text', 'Spracováva sa...'), height=200, key=f"orig_{doc['id']}")
                    with col2:
                        st.subheader("Anonymizovaný text")
                        st.text_area("Anonymized", doc.get('anonymized_text', 'Spracováva sa...'), height=200, key=f"anon_{doc['id']}")
                    st.divider()
            
            # Actions
            if claim['status'] == 'WAITING_FOR_APPROVAL':
                st.subheader("AI Analýza")
                
                # Fetch available prompts
                try:
                    prompts_response = requests.get(f"{BACKEND_URL}/prompts/")
                    if prompts_response.status_code == 200:
                        prompts = prompts_response.json()
                        
                        # Create dropdown options
                        prompt_options = {p['name']: p['id'] for p in prompts}
                        prompt_descriptions = {p['name']: p['description'] for p in prompts}
                        
                        selected_prompt_name = st.selectbox(
                            "Vyberte typ analýzy:",
                            options=list(prompt_options.keys()),
                            key=f"prompt_select_{claim['id']}"
                        )
                        
                        # Show description of selected prompt
                        if selected_prompt_name:
                            st.info(f"ℹ️ {prompt_descriptions[selected_prompt_name]}")
                        
                        selected_prompt_id = prompt_options[selected_prompt_name]
                    else:
                        st.error("Nepodarilo sa načítať zoznam promptov")
                        selected_prompt_id = "default"
                except Exception as e:
                    st.error(f"Chyba pri načítaní promptov: {e}")
                    selected_prompt_id = "default"
                
                if st.button("Schváliť a Analyzovať", key=f"approve_{claim['id']}"):
                    with st.spinner("Analyzujem..."):
                        try:
                            res = requests.post(
                                f"{BACKEND_URL}/approve/{claim['id']}", 
                                json={"prompt_id": selected_prompt_id}
                            )
                            if res.status_code == 200:
                                st.success("Schválené! AI analýza prebieha.")
                                st.rerun()
                            else:
                                st.error(f"Chyba: {res.text}")
                        except Exception as e:
                            st.error(f"Chyba: {e}")
            
            # Analysis Result
            if claim.get('analysis_result'):
                st.divider()
                st.subheader("Výsledok AI Analýzy")
                st.json(claim['analysis_result'])
                result = claim['analysis_result']
                
                # Color code recommendation
                rec = result.get('recommendation', 'UNKNOWN')
                color = "green" if rec == "APPROVE" else "red" if rec == "REJECT" else "orange"
                
                st.markdown(f"### Odporúčanie: :{color}[{rec}]")
                st.markdown(f"**Dôvod:** {result.get('reasoning')}")
                st.markdown(f"**Confidence:** {result.get('confidence')}")
                
                if result.get('missing_info'):
                    st.warning(f"Chýbajúce informácie: {', '.join(result['missing_info'])}")

def main():
    st.sidebar.title("Navigácia")
    page = st.sidebar.radio("Prejsť na:", ["Nahlásenie udalosti", "Admin Dashboard"])
    
    if page == "Nahlásenie udalosti":
        upload_page()
    else:
        admin_dashboard()

if __name__ == "__main__":
    main()
