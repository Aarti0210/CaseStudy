from datetime import datetime, timedelta

from app.models.case import Case
from app.models.hearing import Hearing
from app.models.user import User
from app.extensions import db


class SmartScheduler:
    """Smart scheduling service for hearing optimization."""
    
    @staticmethod
    def suggest_optimal_hearing(case_id):
        """Return a list of up to three suggested hearing slots.

        This is a lightweight placeholder implementation that uses simple heuristics:
        - fetch judges and count their upcoming hearings
        - propose the next available day for each judge
        - score slots inversely with judge workload
        """
        case = Case.query.get(case_id)
        if not case:
            return []

        now = datetime.utcnow()
        suggestions = []

        # query using relationship via Role table since User has role_id not role column
        from app.models.role import Role
        judges = (
            User.query.join(Role)
            .filter(Role.name == "judge")
            .all()
        )
        for judge in judges:
            count = (
                Hearing.query.filter(
                    Hearing.judge_id == judge.id,
                    Hearing.hearing_date >= now,
                )
                .count()
            )
            # propose a slot a few days ahead depending on workload
            slot_time = now + timedelta(days=count + 1)
            suggestions.append(
                {
                    "judge_id": judge.id,
                    "slot": slot_time.isoformat(),
                    "score": 1.0 / (1 + count),
                }
            )

        # sort highest score first and return up to three
        suggestions.sort(key=lambda o: o["score"], reverse=True)
        return suggestions[:3]


# Backward compatibility
suggest_optimal_hearing = SmartScheduler.suggest_optimal_hearing
