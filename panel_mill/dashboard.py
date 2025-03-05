from grafana_foundation_sdk.builders.dashboard import (
    Dashboard as BaseDashboard,
    CustomVariable,
    DatasourceVariable,
)
from grafana_foundation_sdk.models.dashboard import VariableOption
from grafana_foundation_sdk.models.dashboard import VariableHide

from typing import Self


class Dashboard(BaseDashboard):
    def default_variables(
        self,
        tenant: str,
        env_realm_map: dict[str, str] | None = None,
        current_env: str = "prod",
    ) -> Self:
        if env_realm_map is None:
            env_realm_map = {"stage": "nonprod", "prod": "prod"}
        values = ", ".join(f"{env} : {realm}" for env, realm in env_realm_map.items())
        self.with_variable(
            CustomVariable("env")
            .values(values)
            .current(VariableOption(text=current_env, value=env_realm_map[current_env]))
        ).with_variable(
            CustomVariable("project_id")
            .values(f"moz-fx-{tenant}-${{env}}")
            .hide(VariableHide.HIDE_VARIABLE)
        ).with_variable(
            DatasourceVariable("datasource")
            .type_val("prometheus")
            .regex("gcp-v2-$env")
            .hide(VariableHide.HIDE_VARIABLE)
        ).with_variable(
            CustomVariable("namespace")
            .values(f"{tenant}-${{env:text}}")
            .hide(VariableHide.HIDE_VARIABLE)
        )
        return self
