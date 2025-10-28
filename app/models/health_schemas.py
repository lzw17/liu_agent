"""Pydantic schemas for Health Assistant domain."""
from typing import List, Optional
from pydantic import BaseModel, Field
from typing import Dict


class UserProfile(BaseModel):
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    gender: Optional[str] = Field(None, description="Gender")
    age: Optional[int] = Field(None, description="Age")
    height_cm: Optional[float] = Field(None, description="Height in cm")
    weight_kg: Optional[float] = Field(None, description="Weight in kg")
    conditions: List[str] = Field(default_factory=list, description="Chronic conditions")
    allergies: List[str] = Field(default_factory=list, description="Allergies")
    preferences: List[str] = Field(default_factory=list, description="Health preferences and goals")


class PlanItem(BaseModel):
    id: str = Field(...)
    date: str = Field(..., description="YYYY-MM-DD")
    title: str = Field(...)
    category: str = Field(..., description="Category e.g. 运动/饮食/休息/检查/理疗")
    done: bool = Field(False)


class PlanCreate(BaseModel):
    date: str
    title: str
    category: str
    done: Optional[bool] = False


class PlanDoneUpdate(BaseModel):
    done: bool


class CheckinRecord(BaseModel):
    id: str = Field(...)
    date: str = Field(..., description="YYYY-MM-DD")
    type: str = Field(..., description="Check-in type e.g. 体重/步数/血压/睡眠")
    value: str = Field(..., description="Value")


class CheckinCreate(BaseModel):
    date: str
    type: str
    value: str


class RecipeItem(BaseModel):
    id: str = Field(...)
    date: str = Field(..., description="YYYY-MM-DD")
    meal_type: str = Field(..., description="早餐/午餐/晚餐/加餐")
    name: str = Field(...)
    calories: Optional[int] = Field(None)


class RecipeCreate(BaseModel):
    date: str
    meal_type: str
    name: str
    calories: Optional[int] = None


class TherapyItem(BaseModel):
    id: str = Field(...)
    date: str = Field(..., description="YYYY-MM-DD")
    name: str = Field(..., description="Therapy name")
    duration_min: Optional[int] = Field(None)
    notes: Optional[str] = Field(None)


class TherapyCreate(BaseModel):
    date: str
    name: str
    duration_min: Optional[int] = None
    notes: Optional[str] = None


# ---- New: Metrics and Scores ----

class MetricCreate(BaseModel):
    type: str = Field(..., description="Metric type e.g. weight,bmi,heart_rate,bp_systolic,bp_diastolic,steps,sleep_hours,blood_glucose,triglyceride,hdl,ldl,body_fat")
    value: float = Field(..., description="Metric numeric value")
    unit: Optional[str] = Field(None, description="Unit of the metric")
    timestamp: Optional[str] = Field(None, description="ISO timestamp, e.g. 2025-01-01T08:00:00")
    date: Optional[str] = Field(None, description="YYYY-MM-DD; if provided, timestamp will be normalized to this day")
    extra: Optional[Dict] = Field(default=None, description="Additional structured info")


class MetricRecord(MetricCreate):
    id: str = Field(...)
    user_id: Optional[str] = Field(default="user-1")
    timestamp: str = Field(..., description="ISO timestamp")
    date: str = Field(..., description="YYYY-MM-DD")


class ScoreRecord(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    total: float = Field(..., ge=0, le=100)
    subs: Dict[str, float] = Field(default_factory=dict, description="Sub scores e.g. bmi, cardio, sleep, activity")


class ScoreSummary(BaseModel):
    period: str = Field(..., description="e.g. 7d/30d/90d")
    avg_total: float
    best: float
    worst: float
    trend: List[ScoreRecord] = Field(default_factory=list)
