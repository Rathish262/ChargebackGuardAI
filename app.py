
import streamlit as st
import pandas as pd
import joblib

from evidence_engine import EvidenceEngine
from decision_engine import DecisionEngine
from audit_pipeline import AuditPipeline


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


# ==========================================
# INITIALIZE ENGINES
# ==========================================

evidence_engine = EvidenceEngine()

decision_engine = DecisionEngine()

audit_pipeline = AuditPipeline(
    evidence_engine,
    decision_engine
)


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

    # ======================================
    # BUILD CASE
    # ======================================

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


    # ======================================
    # ML PREDICTION
    # ======================================

    X = prepare_features(case)

    ml_prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    ml_confidence = max(probabilities) * 100


    # ======================================
    # COMPLETE AUDIT PIPELINE
    # ======================================

    audit_result = audit_pipeline.analyze(
        case,
        ml_prediction,
        ml_confidence
    )


    # ======================================
    # EXTRACT RESULTS
    # ======================================

    evidence_score = audit_result[
        "evidence_score"
    ]

    evidence_level = audit_result[
        "evidence_level"
    ]

    contradiction = audit_result[
        "contradiction_detected"
    ]

    evidence_reasons = audit_result[
        "evidence_reasons"
    ]

    warnings = audit_result[
        "warnings"
    ]

    evidence_breakdown = audit_result[
        "evidence_breakdown"
    ]

    final_decision = audit_result[
        "final_decision"
    ]

    decision_reason = audit_result[
        "decision_reason"
    ]


    # ======================================
    # AI ANALYSIS RESULT
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
            f"{evidence_score} / 100"
        )

    with col4:

        st.metric(
            "Evidence Level",
            evidence_level
        )


    # ======================================
    # FINAL DECISION
    # ======================================

    st.subheader("⚖️ Final Decision")

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
        decision_reason
    )


    # ======================================
    # CONTRADICTION STATUS
    # ======================================

    st.subheader("🔍 Evidence Consistency")

    if contradiction:

        st.error(
            "⚠️ Contradiction detected in dispute evidence."
        )

    else:

        st.success(
            "✅ No direct contradiction detected."
        )


    # ======================================
    # EVIDENCE ANALYSIS
    # ======================================

    st.subheader("📋 Evidence Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Evidence Reasons")

        if evidence_reasons:

            for item in evidence_reasons:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                "No supporting evidence found."
            )


    with col2:

        st.write("### Warnings")

        if warnings:

            for warning in warnings:

                st.warning(
                    warning
                )

        else:

            st.success(
                "No warnings detected."
            )


    # ======================================
    # EVIDENCE BREAKDOWN
    # ======================================

    st.subheader("📈 Evidence Breakdown")

    breakdown_df = pd.DataFrame(
        {
            "Evidence Type": [
                "Delivery Evidence",
                "Delivery Proof",
                "Refund Evidence",
                "Communication",
                "Consistency"
            ],

            "Score": [
                evidence_breakdown[
                    "delivery_evidence"
                ],

                evidence_breakdown[
                    "delivery_proof"
                ],

                evidence_breakdown[
                    "refund_evidence"
                ],

                evidence_breakdown[
                    "communication_evidence"
                ],

                evidence_breakdown[
                    "consistency"
                ]
            ]
        }
    )

    st.dataframe(
        breakdown_df,
        use_container_width=True,
        hide_index=True
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
    # COMMUNICATION EVIDENCE
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
    # PIPELINE SUMMARY
    # ======================================

    st.subheader("🔗 Decision Pipeline")

    st.write(
        "1️⃣ Machine Learning Prediction"
    )

    st.write(
        "2️⃣ Evidence Analysis"
    )

    st.write(
        "3️⃣ Contradiction Detection"
    )

    st.write(
        "4️⃣ Rule-Based Decision"
    )

    st.write(
        "5️⃣ Final Decision"
    )


    # ======================================
    # SYSTEM STATUS
    # ======================================

    st.divider()

    st.caption(
        "ChargebackGuard AI combines ML prediction, "
        "evidence analysis, contradiction detection "
        "and rule-based safety checks. "
        "This is a decision-support system, not an "
        "automatic payment decision."
    )

