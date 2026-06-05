from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    goal: str = Field(..., min_length=1, max_length=4096, description="The agent's goal in plain language")
    max_steps: int | None = Field(default=None, ge=1, description="Maximum number of steps (default 20)")
    max_cost_usd: float | None = Field(default=None, gt=0, description="Maximum cost budget in USD (default 0.5)")
    scenario: str | None = Field(default=None, description="Mock scenario name for testing")


class ScenarioInfo(BaseModel):
    name: str
    description: str


class RunResponse(BaseModel):
    run_id: str


class StepResponse(BaseModel):
    step_number: int
    tool_name: str | None = None
    args: dict | None = None
    result: dict
    cost: float
    created_at: str | None = None


class RunDetail(BaseModel):
    run_id: str
    goal: str
    status: str
    reason: str | None = None
    total_cost: float
    max_steps: int
    max_cost_usd: float
    started_at: str | None = None
    finished_at: str | None = None
    steps: list[StepResponse] = []


class RunSummary(BaseModel):
    run_id: str
    goal: str
    status: str
    reason: str | None = None
    total_cost: float
    started_at: str | None = None
    finished_at: str | None = None


class RunListResponse(BaseModel):
    runs: list[RunSummary]
    total: int
    limit: int
    offset: int
