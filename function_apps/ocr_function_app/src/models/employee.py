from pydantic import BaseModel
from typing import Optional

class Employee(BaseModel):
    name: str
    alias: str

class Employees(BaseModel):
    employees: list[Employee]

    def find_employee_by_name(self, name: str) -> Optional[Employee]:
            # Search for the employee by name
            for employee in self.employees:
                if employee.name == name:
                    return employee
            return None  # Return None if not found