import streamlit as st
import pandas as pd
import joblib

from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_FILE = "models/chargeback_model.pkl"


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="ChargebackGuard AI",
    page_icon="🛡️",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title("🛡️ ChargebackGuard AI")
st.subheader("AI-Powered Chargeback Decision Support System")

st.write(
    "Analyze a payment dispute using Machine Learning, "
    "Evidence Analysis and Safety Rules."
)

st.divider()


# ==========================================
# LOAD MODEL
# ==========================================

@st.cache_resource
def load_model():

    saved_model = joblib.load(MODEL_FILE)

    if isinstance(saved_model, dict):

        model = saved_model["model"]
        feature_columns = saved_model["feature_columns"]

    else:

        model = saved_model
        feature_columns = None

    return model, feature_columns


model, feature_columns = load_model()

evidence_engine = EvidenceEngine()
decision_engine = DecisionEngine()


# ==========================================
# FEATURE PREPARATION
# ==========================================

def prepare_features(case):

    df = pd.DataFrame([case])

    features = df[
        [
            "amount",
            "delivery_status",
            "delivery_proof",
            "refund_status",
            "reason"
        ]
    ].copy()

    features["delivery_proof"] = (
        features["delivery_proof"]
        .astype(str)
        .map({
            "True": 1,
            "False": 0,
            "true": 1,
            "false": 0
        })
    )

    features = pd.get_dummies(
        features,
        columns=[
            "delivery_status",
            "refund_status",
            "reason"
        ]
    )

    if feature_columns is not None:

        features = features.reindex(
            columns=feature_columns,
            fill_value=0
        )

    return features


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("Dispute Information")

dispute_id = st.sidebar.text_input(
    "Dispute ID",
    "DEMO001"
)

amount = st.sidebar.number_input(
    "Transaction Amount (₹)",
    min_value=0,
    value=5000,
    step=100
)

reason = st.sidebar.selectbox(
    "Dispute Reason",
    [
        "product_not_received",
        "product_not_as_described",
        "unauthorized_transaction",
        "duplicate_charge"
    ]
)

delivery_status = st.sidebar.selectbox(
    "Delivery Status",
    [
        "delivered",
        "failed",
        "unknown"
    ]
)

delivery_proof = st.sidebar.selectbox(
    "Delivery Proof Available?",
    [
        True,
        False
    ]
)

refund_status = st.sidebar.selectbox(
    "Refund Status",
    [
        "not_issued",
        "issued"
    ]
)

customer_message = st.sidebar.text_area(
    "Customer Message",
    "I did not receive my order."
)

merchant_message = st.sidebar.text_area(
    "Merchant Message",
    "Delivery was completed and proof is available."
)


# ==========================================
# ANALYZE BUTTON
# ==========================================

analyze_button = st.button(
    "🔍 Analyze Dispute",
    type="primary",
    use_container_width=True
)


# ==========================================
# ANALYSIS
# ==========================================

if analyze_button:

    case = {

        "dispute_id": dispute_id,

        "amount": amount,

        "reason": reason,

        "delivery_status": delivery_status,

        "delivery_proof": delivery_proof,

        "refund_status": refund_status,

        "customer_message": customer_message,

        "merchant_message": merchant_message
    }


    # --------------------------------------
    # ML PREDICTION
    # --------------------------------------

    X = prepare_features(case)

    ml_prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    ml_confidence = max(probabilities) * 100


    # --------------------------------------
    # EVIDENCE ANALYSIS
    # --------------------------------------

    evidence = evidence_engine.analyze(case)


    # --------------------------------------
    # FINAL DECISION
    # --------------------------------------

    result = decision_engine.decide(
        case,
        ml_prediction
    )


    # ======================================
    # HEADER
    # ======================================

    st.divider()

    st.header("📊 AI Analysis Result")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "ML Prediction",
            ml_prediction
        )

    with col2:

        st.metric(
            "ML Confidence",
            f"{ml_confidence:.1f}%"
        )

    with col3:

        st.metric(
            "Evidence Score",
            f"{evidence['evidence_score']} / 100"
        )

    with col4:

        st.metric(
            "Evidence Level",
            evidence["evidence_level"]
        )


    # ======================================
    # FINAL DECISION
    # ======================================

    st.subheader("⚖️ Final Decision")

    final_decision = result["decision"]

    if final_decision == "CONTEST":

        st.success(
            f"✅ {final_decision}"
        )

    elif final_decision == "DO_NOT_CONTEST":

        st.error(
            f"🛑 {final_decision}"
        )

    else:

        st.warning(
            f"👤 {final_decision}"
        )


    st.write(
        "**Decision Reason:**",
        result["reason"]
    )


    # ======================================
    # EVIDENCE
    # ======================================

    st.subheader("📋 Evidence Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Evidence Reasons")

        if evidence["reasons"]:

            for item in evidence["reasons"]:

                st.write(
                    f"• {item}"
                )

        else:

            st.write("No supporting evidence found.")


    with col2:

        st.write("### Warnings")

        if evidence["warnings"]:

            for warning in evidence["warnings"]:

                st.warning(
                    warning
                )

        else:

            st.success(
                "No contradictions or warnings detected."
            )


    # ======================================
    # CASE DETAILS
    # ======================================

    st.subheader("🧾 Case Details")

    case_data = {

        "Field": [
            "Dispute ID",
            "Amount",
            "Reason",
            "Delivery Status",
            "Delivery Proof",
            "Refund Status"
        ],

        "Value": [
            dispute_id,
            f"₹ {amount}",
            reason,
            delivery_status,
            str(delivery_proof),
            refund_status
        ]
    }

    st.table(
        pd.DataFrame(case_data)
    )


    # ======================================
    # CUSTOMER / MERCHANT MESSAGES
    # ======================================

    st.subheader("💬 Communication Evidence")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Customer Message**")

        st.info(
            customer_message
        )

    with col2:

        st.write("**Merchant Message**")

        st.info(
            merchant_message
        )


    # ======================================
    # SYSTEM STATUS
    # ======================================

    st.divider()

    st.caption(
        "ChargebackGuard AI combines ML prediction, "
        "evidence analysis and rule-based safety checks. "
        "This is a decision-support system, not an automatic payment decision."
    )