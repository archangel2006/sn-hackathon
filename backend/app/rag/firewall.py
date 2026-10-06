from typing import List, Dict, Any, Tuple

class Firewall:
    """
    Enforces role-based document access controls before documents
    are passed to the LLM context or returned to the user.
    """
    @staticmethod
    def filter_documents(docs: List[Dict[str, Any]], role: str) -> Tuple[List[Dict[str, Any]], int]:
        allowed = []
        blocked = 0
        
        is_staff = role in ("staff", "counsellor", "finaid", "advisor", "admin")
        
        for doc in docs:
            doc_audience = doc.get("audience", "student")
            if doc_audience == "staff" and not is_staff:
                blocked += 1
            else:
                allowed.append(doc)
                
        return allowed, blocked

firewall = Firewall()
