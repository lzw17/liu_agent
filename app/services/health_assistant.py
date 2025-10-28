from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from uuid import uuid4
from datetime import datetime, date, timedelta
from ..models.health_schemas import (
    UserProfile,
    PlanItem,
    CheckinRecord,
    RecipeItem,
    TherapyItem,
    MetricCreate,
    MetricRecord,
    ScoreRecord,
)


class HealthAssistantService:
    def __init__(self, storage_path: str = "./data/health_assistant.json"):
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "profile": None,
                "plans": [],
                "checkins": [],
                "recipes": [],
                "therapies": [],
                "metrics": [],
                "scores": []
            }
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_profile(self) -> Optional[UserProfile]:
        data = self._load()
        p = data.get("profile")
        return UserProfile(**p) if p else None

    def set_profile(self, profile: UserProfile) -> UserProfile:
        data = self._load()
        data["profile"] = profile.model_dump()
        self._save(data)
        return profile

    def list_plans(self) -> List[PlanItem]:
        data = self._load()
        return [PlanItem(**x) for x in data.get("plans", [])]

    def add_plan(self, date_str: str, title: str, category: str, done: bool = False) -> PlanItem:
        data = self._load()
        item = PlanItem(id=str(uuid4()), date=date_str, title=title, category=category, done=done)
        data.setdefault("plans", []).append(item.model_dump())
        self._save(data)
        return item

    def set_plan_done(self, plan_id: str, done: bool) -> PlanItem:
        data = self._load()
        plans = data.get("plans", [])
        for p in plans:
            if p.get("id") == plan_id:
                p["done"] = bool(done)
                self._save(data)
                return PlanItem(**p)
        raise ValueError(f"Plan not found: {plan_id}")

    def delete_plan(self, plan_id: str) -> bool:
        data = self._load()
        plans = data.get("plans", [])
        new_plans = [p for p in plans if p.get("id") != plan_id]
        if len(new_plans) == len(plans):
            return False
        data["plans"] = new_plans
        self._save(data)
        return True

    def list_today_plan(self) -> List[PlanItem]:
        today = date.today().isoformat()
        return [p for p in self.list_plans() if p.date == today]

    def list_checkins(self) -> List[CheckinRecord]:
        data = self._load()
        return [CheckinRecord(**x) for x in data.get("checkins", [])]

    def add_checkin(self, date_str: str, type_: str, value: str) -> CheckinRecord:
        data = self._load()
        item = CheckinRecord(id=str(uuid4()), date=date_str, type=type_, value=value)
        data.setdefault("checkins", []).append(item.model_dump())
        self._save(data)
        return item

    def delete_checkin(self, checkin_id: str) -> bool:
        data = self._load()
        arr = data.get("checkins", [])
        new_arr = [x for x in arr if x.get("id") != checkin_id]
        if len(new_arr) == len(arr):
            return False
        data["checkins"] = new_arr
        self._save(data)
        return True

    def list_recipes(self) -> List[RecipeItem]:
        data = self._load()
        return [RecipeItem(**x) for x in data.get("recipes", [])]

    def add_recipe(self, date_str: str, meal_type: str, name: str, calories: Optional[int] = None) -> RecipeItem:
        data = self._load()
        item = RecipeItem(id=str(uuid4()), date=date_str, meal_type=meal_type, name=name, calories=calories)
        data.setdefault("recipes", []).append(item.model_dump())
        self._save(data)
        return item

    def delete_recipe(self, recipe_id: str) -> bool:
        data = self._load()
        arr = data.get("recipes", [])
        new_arr = [x for x in arr if x.get("id") != recipe_id]
        if len(new_arr) == len(arr):
            return False
        data["recipes"] = new_arr
        self._save(data)
        return True

    def list_therapies(self) -> List[TherapyItem]:
        data = self._load()
        return [TherapyItem(**x) for x in data.get("therapies", [])]

    def add_therapy(self, date_str: str, name: str, duration_min: Optional[int] = None, notes: Optional[str] = None) -> TherapyItem:
        data = self._load()
        item = TherapyItem(id=str(uuid4()), date=date_str, name=name, duration_min=duration_min, notes=notes)
        data.setdefault("therapies", []).append(item.model_dump())
        self._save(data)
        return item

    def delete_therapy(self, therapy_id: str) -> bool:
        data = self._load()
        arr = data.get("therapies", [])
        new_arr = [x for x in arr if x.get("id") != therapy_id]
        if len(new_arr) == len(arr):
            return False
        data["therapies"] = new_arr
        self._save(data)
        return True

    def add_metric(self, m: MetricCreate) -> MetricRecord:
        data = self._load()
        ts = m.timestamp or (m.date + "T08:00:00" if m.date else datetime.now().isoformat())
        d = m.date or (m.timestamp[:10] if m.timestamp else datetime.now().date().isoformat())
        rec = MetricRecord(id=str(uuid4()), user_id="user-1", type=m.type, value=float(m.value), unit=m.unit, timestamp=ts, date=d, extra=m.extra)
        data.setdefault("metrics", []).append(rec.model_dump())
        if rec.type == "weight":
            prof = data.get("profile")
            h = None
            if prof and prof.get("height_cm"):
                h = prof["height_cm"]/100.0
            if h and h > 0:
                bmi = rec.value/(h*h)
                bmi_rec = MetricRecord(id=str(uuid4()), user_id=rec.user_id, type="bmi", value=round(bmi,2), unit=None, timestamp=rec.timestamp, date=rec.date, extra=None)
                data.setdefault("metrics", []).append(bmi_rec.model_dump())
        self._save(data)
        return rec

    def delete_metric(self, metric_id: str) -> bool:
        data = self._load()
        arr = data.get("metrics", [])
        new_arr = [x for x in arr if x.get("id") != metric_id]
        if len(new_arr) == len(arr):
            return False
        data["metrics"] = new_arr
        self._save(data)
        return True

    def add_metrics(self, items: List[MetricCreate]) -> List[MetricRecord]:
        out: List[MetricRecord] = []
        for m in items:
            out.append(self.add_metric(m))
        return out

    def list_metrics(self, type_: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> List[MetricRecord]:
        data = self._load()
        arr = [MetricRecord(**x) for x in data.get("metrics", [])]
        if type_:
            arr = [x for x in arr if x.type == type_]
        if start:
            arr = [x for x in arr if x.date >= start]
        if end:
            arr = [x for x in arr if x.date <= end]
        arr.sort(key=lambda x: (x.date, x.timestamp))
        return arr

    def metrics_series(self, types: List[str], start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        out: Dict[str, List[Dict[str, Any]]] = {}
        for t in types:
            arr = self.list_metrics(t, start, end)
            out[t] = [{"date": x.date, "timestamp": x.timestamp, "value": x.value} for x in arr]
        return out

    def _latest_metric(self, type_: str, date_str: str) -> Optional[MetricRecord]:
        arr = self.list_metrics(type_, date_str, date_str)
        return arr[-1] if arr else None

    def _sub_bmi(self, bmi: Optional[float]) -> float:
        if bmi is None:
            return 0.0
        if 18.5 <= bmi <= 24:
            return 100.0
        if bmi < 18.5:
            diff = 18.5 - bmi
            s = 100.0 - diff * 12.0
            return max(0.0, min(100.0, s))
        diff = bmi - 24.0
        s = 100.0 - diff * 10.0
        return max(0.0, min(100.0, s))

    def _sub_cardio(self, hr: Optional[float], sys: Optional[float], dia: Optional[float]) -> float:
        parts: List[float] = []
        if hr is not None:
            if 60 <= hr <= 90:
                parts.append(100.0)
            else:
                parts.append(max(0.0, 100.0 - abs(hr - 75.0) * 3.0))
        if sys is not None:
            parts.append(max(0.0, 100.0 - abs(sys - 115.0) * 1.5))
        if dia is not None:
            parts.append(max(0.0, 100.0 - abs(dia - 75.0) * 2.0))
        if not parts:
            return 0.0
        return sum(parts) / len(parts)

    def _sub_sleep(self, hours: Optional[float]) -> float:
        if hours is None:
            return 0.0
        if 7.0 <= hours <= 9.0:
            return 100.0
        if hours < 7.0:
            return max(0.0, 100.0 - (7.0 - hours) * 20.0)
        return max(0.0, 100.0 - (hours - 9.0) * 15.0)

    def _sub_activity(self, steps: Optional[float]) -> float:
        if steps is None:
            return 0.0
        target = 8000.0
        score = steps / target * 100.0
        return max(0.0, min(100.0, score))

    def compute_score(self, date_str: Optional[str] = None) -> ScoreRecord:
        d = date_str or datetime.now().date().isoformat()
        data = self._load()
        prof = data.get("profile") or {}
        h_cm = prof.get("height_cm")
        h_m = h_cm / 100.0 if h_cm else None

        # --- Base components (same as before) ---
        weight = self._latest_metric("weight", d)
        bmi_metric = self._latest_metric("bmi", d)
        hr = self._latest_metric("heart_rate", d)
        sys = self._latest_metric("bp_systolic", d)
        dia = self._latest_metric("bp_diastolic", d)
        steps = self._latest_metric("steps", d)
        sleep = self._latest_metric("sleep_hours", d)
        bmi_val: Optional[float] = None
        if bmi_metric:
            bmi_val = bmi_metric.value
        elif weight and h_m and h_m > 0:
            bmi_val = round(weight.value / (h_m * h_m), 2)
        bmi_s = self._sub_bmi(bmi_val)
        cardio_s = self._sub_cardio(hr.value if hr else None, sys.value if sys else None, dia.value if dia else None)
        sleep_s = self._sub_sleep(sleep.value if sleep else None)
        act_s = self._sub_activity(steps.value if steps else None)
        base_total = round(bmi_s * 0.3 + cardio_s * 0.3 + sleep_s * 0.2 + act_s * 0.2, 2)

        # --- Plan completion influence ---
        plans = data.get("plans", [])
        today_plans = [p for p in plans if p.get("date") == d]
        plan_ratio: Optional[float] = None
        if today_plans:
            done_cnt = sum(1 for p in today_plans if bool(p.get("done")))
            total_cnt = len(today_plans)
            plan_ratio = done_cnt / total_cnt if total_cnt > 0 else None
        # bonus from -10 to +10, neutral at 50% completion; if no plans, neutral 0
        plan_bonus = 0.0 if plan_ratio is None else (plan_ratio - 0.5) * 20.0

        # --- Trend adjustment vs previous day ---
        prev_d = (datetime.fromisoformat(d).date() - timedelta(days=1)).isoformat()
        prev_total: Optional[float] = None
        # Prefer stored previous total if available
        prev_scores = [x for x in data.get("scores", []) if x.get("date") == prev_d]
        if prev_scores:
            try:
                prev_total = float(prev_scores[-1].get("total"))
            except Exception:
                prev_total = None
        if prev_total is None:
            # compute previous base total without saving
            pw = self._latest_metric("weight", prev_d)
            pbmi_m = self._latest_metric("bmi", prev_d)
            phr = self._latest_metric("heart_rate", prev_d)
            psys = self._latest_metric("bp_systolic", prev_d)
            pdia = self._latest_metric("bp_diastolic", prev_d)
            psteps = self._latest_metric("steps", prev_d)
            psleep = self._latest_metric("sleep_hours", prev_d)
            pbmi_val: Optional[float] = None
            if pbmi_m:
                pbmi_val = pbmi_m.value
            elif pw and h_m and h_m > 0:
                pbmi_val = round(pw.value / (h_m * h_m), 2)
            pbmi_s = self._sub_bmi(pbmi_val)
            pcardio_s = self._sub_cardio(phr.value if phr else None, psys.value if psys else None, pdia.value if pdia else None)
            psleep_s = self._sub_sleep(psleep.value if psleep else None)
            pact_s = self._sub_activity(psteps.value if psteps else None)
            prev_total = round(pbmi_s * 0.3 + pcardio_s * 0.3 + psleep_s * 0.2 + pact_s * 0.2, 2)

        # diff scaled to +/-5 max
        trend_bonus = 0.0
        if prev_total is not None:
            diff = base_total - prev_total
            trend_bonus = max(-5.0, min(5.0, diff * 0.2))

        final_total = base_total + plan_bonus + trend_bonus
        final_total = max(0.0, min(100.0, round(final_total, 2)))

        subs = {
            "bmi": round(bmi_s, 2),
            "cardio": round(cardio_s, 2),
            "sleep": round(sleep_s, 2),
            "activity": round(act_s, 2),
            "base": base_total,
        }
        if plan_ratio is not None:
            subs["plan_completion"] = round(plan_ratio * 100.0, 1)  # percentage
            subs["plan_bonus"] = round(plan_bonus, 2)
        if prev_total is not None:
            subs["prev_total"] = round(prev_total, 2)
            subs["trend_bonus"] = round(trend_bonus, 2)

        rec = ScoreRecord(date=d, total=final_total, subs=subs)
        scores = data.setdefault("scores", [])
        scores = [x for x in scores if x.get("date") != d]
        scores.append(rec.model_dump())
        data["scores"] = scores
        self._save(data)
        return rec

    def score_history(self, days: int = 30) -> List[ScoreRecord]:
        out: List[ScoreRecord] = []
        today = datetime.now().date()
        for i in range(days):
            d = (today - timedelta(days=i)).isoformat()
            out.append(self.compute_score(d))
        out.sort(key=lambda x: x.date)
        return out

    def generate_plan(self, date_str: Optional[str] = None) -> List[PlanItem]:
        d = date_str or datetime.now().date().isoformat()
        created: List[PlanItem] = []
        created.append(self.add_plan(d, "快走30分钟或慢跑20分钟", "运动", False))
        created.append(self.add_plan(d, "三餐规律，控制油盐糖，优先高蛋白与蔬果", "饮食", False))
        created.append(self.add_plan(d, "23:00前就寝，午间小憩15分钟", "休息", False))
        created.append(self.add_plan(d, "饮水1500-2000ml，拉伸10分钟", "检查", False))
        created.append(self.add_plan(d, "睡前泡脚20分钟或肩颈放松", "理疗", False))
        return created

    def generate_recipes(self, date_str: Optional[str] = None) -> List[RecipeItem]:
        d = date_str or datetime.now().date().isoformat()
        out: List[RecipeItem] = []
        out.append(self.add_recipe(d, "早餐", "燕麦牛奶+水煮蛋+水果", 450))
        out.append(self.add_recipe(d, "午餐", "清蒸鱼+糙米饭+西兰花", 650))
        out.append(self.add_recipe(d, "晚餐", "鸡胸肉沙拉+紫菜蛋花汤", 550))
        return out

    def generate_therapies(self, date_str: Optional[str] = None) -> List[TherapyItem]:
        d = date_str or datetime.now().date().isoformat()
        out: List[TherapyItem] = []
        out.append(self.add_therapy(d, "热水泡脚", 20, None))
        out.append(self.add_therapy(d, "肩颈放松", 10, None))
        out.append(self.add_therapy(d, "冥想呼吸", 10, None))
        return out

    def adjust_plans(self, date_str: Optional[str] = None) -> List[PlanItem]:
        d = date_str or datetime.now().date().isoformat()
        sc = self.compute_score(d)
        plans = self.list_plans()
        today = [p for p in plans if p.date == d]
        if sc.total < 60:
            self.add_plan(d, "增加步行到45分钟，晚间减少精制糖", "运动", False)
        else:
            self.add_plan(d, "维持当前强度，注意补水与拉伸", "休息", False)
        return [p for p in self.list_plans() if p.date == d]


_service_instance: Optional[HealthAssistantService] = None


def get_health_assistant_service() -> HealthAssistantService:
    global _service_instance
    if _service_instance is None:
        _service_instance = HealthAssistantService()
    return _service_instance
