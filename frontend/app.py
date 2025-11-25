import streamlit as st
import requests
import os
import json

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="AI Claims Processing", layout="wide")


def upload_page():
    """User-facing page for uploading claim documents"""
    st.header("Nahlásenie poistnej udalosti")
    st.write("Nahrajte dokumenty k vašej poistnej udalosti (PDF).")
    
    # Country selection
    country = st.selectbox(
        "Vyberte krajinu:",
        options=["SK", "IT", "DE"],
        index=0,
        help="Vyberte krajinu pre správnu anonymizáciu"
    )
    
    uploaded_files = st.file_uploader(
        "Vyberte súbory",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Odoslať"):
            with st.spinner("Nahrávam súbory..."):
                try:
                    files = [("files", (file.name, file, file.type)) for file in uploaded_files]
                    response = requests.post(
                        f"{BACKEND_URL}/upload/",
                        files=files,
                        params={"country": country}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Súbory úspešne nahrané! Vytvorený nárok ID: {data['id']}")
                        st.info("Váš nárok sa spracováva. Prosím čakajte na vyjadrenie.")
                    else:
                        st.error(f"Chyba pri nahrávaní: {response.text}")
                except Exception as e:
                    st.error(f"Nepodarilo sa pripojiť k serveru: {e}")


def ocr_review_page():
    """OCR Review HITL page"""
    st.header("OCR Review - Kontrola extrahovaného textu")
    
    # Fetch claims in OCR_REVIEW status
    try:
        response = requests.get(f"{BACKEND_URL}/claims/")
        if response.status_code == 200:
            all_claims = response.json()
            ocr_claims = [c for c in all_claims if c['status'] == 'OCR_REVIEW']
        else:
            st.error("Nepodarilo sa načítať zoznam claimov.")
            return
    except Exception as e:
        st.error(f"Chyba pripojenia: {e}")
        return
    
    if not ocr_claims:
        st.info("Žiadne claimy čakajúce na OCR review.")
        return
    
    # Claim selector
    claim_ids = [f"Claim #{c['id']} ({c['country']})" for c in ocr_claims]
    selected_idx = st.selectbox("Vyberte claim:", range(len(claim_ids)), format_func=lambda i: claim_ids[i])
    
    if selected_idx is not None:
        claim = ocr_claims[selected_idx]
        st.write(f"**Claim ID:** {claim['id']}")
        st.write(f"**Krajina:** {claim['country']}")
        st.write(f"**Vytvorené:** {claim['created_at']}")
        
        st.divider()
        
        # Editable text areas for each document
        edits = {}
        for doc in claim['documents']:
            st.subheader(f"📄 {doc['filename']}")
            original_text = doc.get('original_text', '')
            
            edited_text = st.text_area(
                f"Text z OCR (editovateľný):",
                value=original_text,
                height=300,
                key=f"ocr_edit_{doc['id']}"
            )
            
            if edited_text != original_text:
                edits[str(doc['id'])] = edited_text
                st.info("✏️ Text bol upravený")
            
            st.divider()
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if edits and st.button("💾 Uložiť zmeny", type="primary"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/claims/{claim['id']}/ocr-edit",
                        json=edits
                    )
                    if response.status_code == 200:
                        st.success("Zmeny uložené!")
                        st.rerun()
                    else:
                        st.error(f"Chyba: {response.text}")
                except Exception as e:
                    st.error(f"Chyba: {e}")
        
        with col2:
            if st.button("✅ Schváliť a pokračovať", type="primary"):
                try:
                    # Save edits first if any
                    if edits:
                        requests.post(
                            f"{BACKEND_URL}/claims/{claim['id']}/ocr-edit",
                            json=edits
                        )
                    
                    # Approve
                    response = requests.post(f"{BACKEND_URL}/claims/{claim['id']}/ocr-approve")
                    if response.status_code == 200:
                        st.success("OCR schválené! Prebieha čistenie dát...")
                        st.rerun()
                    else:
                        st.error(f"Chyba: {response.text}")
                except Exception as e:
                    st.error(f"Chyba: {e}")


def anon_review_page():
    """Anonymization Review HITL page"""
    st.header("Anonymization Review - Kontrola anonymizácie")
    
    # Fetch claims in ANONYMIZATION_REVIEW status
    try:
        response = requests.get(f"{BACKEND_URL}/claims/")
        if response.status_code == 200:
            all_claims = response.json()
            anon_claims = [c for c in all_claims if c['status'] == 'ANONYMIZATION_REVIEW']
        else:
            st.error("Nepodarilo sa načítať zoznam claimov.")
            return
    except Exception as e:
        st.error(f"Chyba pripojenia: {e}")
        return
    
    if not anon_claims:
        st.info("Žiadne claimy čakajúce na anonymization review.")
        return
    
    # Claim selector
    claim_ids = [f"Claim #{c['id']} ({c['country']})" for c in anon_claims]
    selected_idx = st.selectbox("Vyberte claim:", range(len(claim_ids)), format_func=lambda i: claim_ids[i])
    
    if selected_idx is not None:
        claim = anon_claims[selected_idx]
        st.write(f"**Claim ID:** {claim['id']}")
        st.write(f"**Krajina:** {claim['country']}")
        
        st.divider()
        
        # Side-by-side comparison for each document
        edits = {}
        for doc in claim['documents']:
            st.subheader(f"📄 {doc['filename']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Vyčistený text:**")
                st.text_area(
                    "Cleaned",
                    value=doc.get('cleaned_text', ''),
                    height=250,
                    key=f"cleaned_{doc['id']}",
                    disabled=True
                )
            
            with col2:
                st.markdown("**Anonymizovaný text (editovateľný):**")
                anonymized_text = doc.get('anonymized_text', '')
                edited_text = st.text_area(
                    "Anonymized",
                    value=anonymized_text,
                    height=250,
                    key=f"anon_edit_{doc['id']}"
                )
                
                if edited_text != anonymized_text:
                    edits[str(doc['id'])] = edited_text
                    st.info("✏️ Text bol upravený")
            
            st.divider()
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if edits and st.button("💾 Uložiť zmeny", type="primary"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/claims/{claim['id']}/anon-edit",
                        json=edits
                    )
                    if response.status_code == 200:
                        st.success("Zmeny uložené!")
                        st.rerun()
                    else:
                        st.error(f"Chyba: {response.text}")
                except Exception as e:
                    st.error(f"Chyba: {e}")
        
        with col2:
            if st.button("✅ Schváliť pre analýzu", type="primary"):
                try:
                    # Save edits first if any
                    if edits:
                        requests.post(
                            f"{BACKEND_URL}/claims/{claim['id']}/anon-edit",
                            json=edits
                        )
                    
                    # Approve
                    response = requests.post(f"{BACKEND_URL}/claims/{claim['id']}/anon-approve")
                    if response.status_code == 200:
                        st.success("Anonymizácia schválená! Claim pripravený na analýzu.")
                        st.rerun()
                    else:
                        st.error(f"Chyba: {response.text}")
                except Exception as e:
                    st.error(f"Chyba: {e}")


def rag_management_page():
    """RAG Document Management page"""
    st.header("RAG Management - Správa policy dokumentov")
    
    tab1, tab2 = st.tabs(["📤 Nahrať dokumenty", "📚 Prehľad dokumentov"])
    
    with tab1:
        st.subheader("Nahrať nový policy dokument")
        
        col1, col2 = st.columns(2)
        
        with col1:
            country = st.selectbox(
                "Krajina:",
                options=["SK", "IT", "DE"],
                index=0,
                key="rag_country"
            )
        
        with col2:
            document_type = st.text_input(
                "Typ dokumentu:",
                value="vseobecne-podmienky",
                help="Napr.: vseobecne-podmienky, zdravotne, generale, allgemein"
            )
        
        uploaded_file = st.file_uploader(
            "Vyberte PDF dokument:",
            type=['pdf'],
            key="rag_upload"
        )
        
        if uploaded_file and st.button("📤 Nahrať", type="primary"):
            with st.spinner("Nahrávam dokument..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    data = {
                        "country": country,
                        "document_type": document_type
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/rag/upload",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Dokument nahraný! ID: {result['id']}")
                        st.info("Dokument sa spracováva (OCR + embeddings)...")
                    else:
                        st.error(f"Chyba: {response.text}")
                except Exception as e:
                    st.error(f"Chyba: {e}")
    
    with tab2:
        st.subheader("Existujúce dokumenty")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_country = st.selectbox(
                "Filtrovať podľa krajiny:",
                options=["Všetky", "SK", "IT", "DE"],
                index=0
            )
        
        with col2:
            # Get folder structure
            try:
                structure_response = requests.get(f"{BACKEND_URL}/rag/structure")
                if structure_response.status_code == 200:
                    structure = structure_response.json()
                    all_doc_types = []
                    for country_types in structure.values():
                        all_doc_types.extend(country_types)
                    unique_types = list(set(all_doc_types))
                    
                    filter_doc_type = st.selectbox(
                        "Filtrovať podľa typu:",
                        options=["Všetky"] + unique_types,
                        index=0
                    )
                else:
                    filter_doc_type = "Všetky"
            except:
                filter_doc_type = "Všetky"
        
        # Fetch documents
        try:
            params = {}
            if filter_country != "Všetky":
                params["country"] = filter_country
            if filter_doc_type != "Všetky":
                params["document_type"] = filter_doc_type
            
            response = requests.get(f"{BACKEND_URL}/rag/documents", params=params)
            
            if response.status_code == 200:
                docs = response.json()
                
                if not docs:
                    st.info("Žiadne dokumenty.")
                else:
                    st.write(f"**Počet dokumentov:** {len(docs)}")
                    
                    # Display as table
                    for doc in docs:
                        with st.expander(f"📄 {doc['filename']} ({doc['country']}/{doc['document_type']})"):
                            st.write(f"**ID:** {doc['id']}")
                            st.write(f"**Krajina:** {doc['country']}")
                            st.write(f"**Typ:** {doc['document_type']}")
                            st.write(f"**Nahrané:** {doc['created_at']}")
                            st.write(f"**Nahrál:** {doc['uploaded_by']}")
                            
                            if st.button("🗑️ Zmazať", key=f"delete_rag_{doc['id']}"):
                                try:
                                    del_response = requests.delete(
                                        f"{BACKEND_URL}/rag/documents/{doc['id']}"
                                    )
                                    if del_response.status_code == 200:
                                        st.success("Dokument zmazaný!")
                                        st.rerun()
                                    else:
                                        st.error(f"Chyba: {del_response.text}")
                                except Exception as e:
                                    st.error(f"Chyba: {e}")
            else:
                st.error("Nepodarilo sa načítať dokumenty.")
        except Exception as e:
            st.error(f"Chyba: {e}")


def admin_dashboard():
    """Enhanced Admin Dashboard with new workflow"""
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
    
    # Status summary
    status_counts = {}
    for claim in claims:
        status = claim['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    st.write("**Prehľad statusov:**")
    cols = st.columns(len(status_counts))
    for idx, (status, count) in enumerate(status_counts.items()):
        with cols[idx]:
            st.metric(status, count)
    
    st.divider()
    
    # List view
    for claim in claims:
        # Status color
        status = claim['status']
        color = "🔵" if status == "PROCESSING" else "🟡" if "REVIEW" in status else "🟢" if status == "ANALYZED" else "⚪"
        
        with st.expander(f"{color} Claim #{claim['id']} - {status} ({claim.get('country', 'N/A')})"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**ID:** {claim['id']}")
                st.write(f"**Krajina:** {claim.get('country', 'N/A')}")
            with col2:
                st.write(f"**Status:** {status}")
                st.write(f"**Vytvorené:** {claim['created_at']}")
            with col3:
                st.write(f"**Dokumenty:** {len(claim.get('documents', []))}")
                if claim.get('analysis_model'):
                    st.write(f"**Model:** {claim['analysis_model']}")
            
            st.divider()
            
            # Retry button for stuck claims
            if status in ['ANONYMIZING', 'CLEANING']:
                st.warning(f"⚠️ Claim je v stave {status}. Ak je zaseknutý, môžete skúsiť znovu spustiť spracovanie.")
                
                if st.button(f"🔄 Retry {status}", key=f"retry_{claim['id']}", type="secondary"):
                    with st.spinner(f"Reštartujem {status.lower()}..."):
                        try:
                            response = requests.post(f"{BACKEND_URL}/claims/{claim['id']}/retry-anonymization")
                            if response.status_code == 200:
                                result = response.json()
                                st.success(f"✅ {result['message']}")
                                st.rerun()
                            else:
                                st.error(f"Chyba: {response.text}")
                        except Exception as e:
                            st.error(f"Chyba: {e}")
            
            # Reset Analysis Status
            if status == 'ANALYZING' or status == 'FAILED':
                st.warning(f"⚠️ Claim je v stave {status}. Ak analýza trvá príliš dlho, môžete ju reštartovať.")
                
                if st.button(f"🔄 Reset Status", key=f"reset_{claim['id']}", type="secondary"):
                    with st.spinner("Resetujem status..."):
                        try:
                            response = requests.post(f"{BACKEND_URL}/claims/{claim['id']}/reset-status")
                            if response.status_code == 200:
                                st.success("Status resetovaný! Teraz môžete znovu spustiť analýzu.")
                                st.rerun()
                            else:
                                st.error(f"Chyba: {response.text}")
                        except Exception as e:
                            st.error(f"Chyba: {e}")
            
            # Documents
            st.subheader("📄 Dokumenty")
            if 'documents' in claim:
                for doc in claim['documents']:
                    with st.expander(f"📎 {doc['filename']}"):
                        if doc.get('original_text'):
                            st.text_area("Original Text", doc['original_text'][:500] + "...", height=100, disabled=True, key=f"orig_{claim['id']}_{doc['id']}")
                        if doc.get('anonymized_text'):
                            st.text_area("Anonymized Text", doc['anonymized_text'][:500] + "...", height=100, disabled=True, key=f"anon_{claim['id']}_{doc['id']}")
            
            # Analysis action
            if status == 'READY_FOR_ANALYSIS':
                st.subheader("🤖 AI Analýza")
                
                try:
                    prompts_response = requests.get(f"{BACKEND_URL}/prompts-config/")
                    if prompts_response.status_code == 200:
                        prompts = prompts_response.json()
                        prompt_options = {p['name']: p['id'] for p in prompts}
                        prompt_descriptions = {p['name']: p['description'] for p in prompts}
                        
                        selected_prompt_name = st.selectbox(
                            "Vyberte typ analýzy:",
                            options=list(prompt_options.keys()),
                            key=f"prompt_select_{claim['id']}"
                        )
                        
                        if selected_prompt_name:
                            st.info(f"ℹ️ {prompt_descriptions[selected_prompt_name]}")
                        
                        selected_prompt_id = prompt_options[selected_prompt_name]
                    else:
                        selected_prompt_id = "default"
                except Exception as e:
                    st.error(f"Chyba pri načítaní promptov: {e}")
                    selected_prompt_id = "default"
                
                if st.button("🚀 Spustiť analýzu", key=f"analyze_{claim['id']}", type="primary"):
                    with st.spinner("Spúšťam analýzu..."):
                        try:
                            res = requests.post(
                                f"{BACKEND_URL}/analyze/{claim['id']}",
                                json={"prompt_id": selected_prompt_id}
                            )
                            if res.status_code == 200:
                                st.success("Analýza spustená!")
                                st.rerun()
                            else:
                                st.error(f"Chyba: {res.text}")
                        except Exception as e:
                            st.error(f"Chyba: {e}")
            
            # Analysis result
            if claim.get('analysis_result'):
                st.divider()
                st.subheader("📊 Výsledok AI Analýzy")
                
                result = claim['analysis_result']
                rec = result.get('recommendation', 'UNKNOWN')
                confidence = result.get('confidence', 0)
                
                # Color-coded recommendation
                if rec == "APPROVE":
                    st.success(f"✅ Odporúčanie: **{rec}**")
                elif rec == "REJECT":
                    st.error(f"❌ Odporúčanie: **{rec}**")
                else:
                    st.warning(f"⚠️ Odporúčanie: **{rec}**")
                
                st.metric("Confidence", f"{confidence*100:.1f}%")
                
                st.markdown("**Reasoning:**")
                st.write(result.get('reasoning', 'N/A'))
                
                if result.get('missing_info'):
                    st.warning(f"**Chýbajúce informácie:** {', '.join(result['missing_info'])}")
                
                # Additional fields (fraud, medical)
                if result.get('fraud_risk_score'):
                    st.metric("Fraud Risk Score", f"{result['fraud_risk_score']*100:.1f}%")
                if result.get('red_flags'):
                    st.error(f"**Red Flags:** {', '.join(result['red_flags'])}")
                if result.get('medical_codes_found'):
                    st.info(f"**Medical Codes:** {', '.join(result['medical_codes_found'])}")
                
                # Download report
                try:
                    reports_response = requests.get(f"{BACKEND_URL}/claims/{claim['id']}/reports")
                    if reports_response.status_code == 200:
                        reports = reports_response.json()
                        if reports:
                            st.divider()
                            st.subheader("📄 Reporty")
                            for report in reports:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Created:** {report['created_at']}")
                                    st.write(f"**Model:** {report['model_used']}")
                                with col2:
                                    # Get download URL
                                    try:
                                        dl_response = requests.get(
                                            f"{BACKEND_URL}/reports/{report['id']}/download"
                                        )
                                        if dl_response.status_code == 200:
                                            dl_url = dl_response.json()['download_url']
                                            st.link_button("⬇️ Stiahnuť PDF", dl_url)
                                    except:
                                        pass
                except:
                    pass


def main():
    st.sidebar.title("🏥 AI Claims Processing")
    
    page = st.sidebar.radio(
        "Navigácia:",
        [
            "🏠 Nahlásenie udalosti",
            "🔍 OCR Review",
            "🔒 Anonymization Review",
            "📊 Admin Dashboard",
            "📚 RAG Management"
        ]
    )
    
    if page == "🏠 Nahlásenie udalosti":
        upload_page()
    elif page == "🔍 OCR Review":
        ocr_review_page()
    elif page == "🔒 Anonymization Review":
        anon_review_page()
    elif page == "📊 Admin Dashboard":
        admin_dashboard()
    elif page == "📚 RAG Management":
        rag_management_page()


if __name__ == "__main__":
    main()
