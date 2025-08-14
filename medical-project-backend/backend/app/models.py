from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime
from pydantic import ConfigDict


class HistoryCreate(BaseModel):
    diagnostic: str = Field(
        ...,
        json_schema_extra={"example": "Hypertension"}
    )
    treatment: str = Field(
        ...,
        json_schema_extra={"example": "Angiotensin II receptor blockers"}
    )
    doctor_id: Optional[str] = Field(
        None,
        json_schema_extra={"example": "2d3cfc26-4958-4723-acf8-9799502c4d7d"}
    )
    doctor_first_name: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Alice"}
    )
    doctor_last_name: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Brown"}
    )
    start_date: date = Field(
        ...,
        json_schema_extra={"example": "1995-07-15"}
    )
    end_date: Optional[date] = Field(
        None,
        json_schema_extra={"example": "1995-09-12"}
    )

    model_config = ConfigDict(from_attributes=True)


class ParentCreate(BaseModel):
    first_name: str = Field(
        ...,
        json_schema_extra={"example": "Alice"}
    )
    last_name: str = Field(
        ...,
        json_schema_extra={"example": "Johnson"}
    )
    phone_number: str = Field(
        ...,
        json_schema_extra={"example": "123-456-7890"}
    )
    email: str = Field(
        ...,
        json_schema_extra={"example": "alice@email.com"}
    )
    gender: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Male"}
    )

    model_config = ConfigDict(from_attributes=True)


class HistoryUpdate(BaseModel):
    diagnostic: str = Field(
        ...,
        json_schema_extra={"example": "Hypertension"}
    )
    treatment: str = Field(
        ...,
        json_schema_extra={"example": "Angiotensin II receptor blockers"}
    )
    doctor_id: str = Field(
        ...,
        json_schema_extra={"example": "2d3cfc26-4958-4723-acf8-9799502c4d7d"}
    )
    start_date: date = Field(
        ...,
        json_schema_extra={"example": "1995-07-15"}
    )
    end_date: date = Field(
        ...,
        json_schema_extra={"example": "1995-09-12"}
    )

    model_config = ConfigDict(from_attributes=True)


class VisitCreate(BaseModel):
    establishment_id: Optional[str] = Field(
        None,
        json_schema_extra={"example": "e1234567-89ab-cdef-0123-456789abcdef"}
    )
    establishment_name: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Central City Hospital"}
    )
    doctor_id: Optional[str] = Field(
        None,
        json_schema_extra={"example": "2d3cfc26-4958-4723-acf8-9799502c4d7d"}
    )
    doctor_first_name: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Alice"}
    )
    doctor_last_name: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Brown"}
    )
    visit_date: date = Field(
        ...,
        json_schema_extra={"example": "2022-02-20"}
    )
    diagnostic: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Common cold with mild fever"}
    )
    treatment: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "Rest, hydration, and over-the-counter pain relievers"}
    )
    summary: str = Field(
        ...,
        json_schema_extra={
            "example": "Patient presented with cold symptoms. Recommended home care and rest."}
    )
    notes: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "Follow-up in one week if symptoms persist"}
    )

    model_config = ConfigDict(from_attributes=True)


class VisitUpdate(BaseModel):
    establishment_id: str = Field(
        ...,
        json_schema_extra={"example": "e1234567-89ab-cdef-0123-456789abcdef"}
    )
    doctor_id: str = Field(
        ...,
        json_schema_extra={"example": "2d3cfc26-4958-4723-acf8-9799502c4d7d"}
    )
    visit_date: date = Field(
        ...,
        json_schema_extra={"example": "2022-02-20"}
    )
    diagnostic: Optional[str] = Field(
        ...,
        json_schema_extra={"example": "Common cold with mild fever"}
    )
    treatment: Optional[str] = Field(
        ...,
        json_schema_extra={
            "example": "Rest, hydration, and over-the-counter pain relievers"}
    )
    summary: str = Field(
        ...,
        json_schema_extra={
            "example": "Patient presented with cold symptoms. Recommended home care and rest."}
    )
    notes: Optional[str] = Field(
        ...,
        json_schema_extra={
            "example": "Follow-up in one week if symptoms persist"}
    )

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    user_id: str
    login: str
    user_type: str
    first_name: str
    last_name: str
    phone_number: str
    email: str
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DoctorResponse(BaseModel):
    id: str
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class CoordinateCreate(BaseModel):
    street_address: str = Field(
        ...,
        json_schema_extra={"example": "123 Main St"}
    )
    apartment: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Apt 4B"}
    )
    postal_code: str = Field(
        ...,
        json_schema_extra={"example": "12345"}
    )
    city: str = Field(
        ...,
        json_schema_extra={"example": "Anytown"}
    )
    country: str = Field(
        ...,
        json_schema_extra={"example": "USA"}
    )

    model_config = ConfigDict(from_attributes=True)


class ParentsCreate(BaseModel):
    parent_id: str = Field(
        ...,
        json_schema_extra={"example": "99febb18-8a4c-40b6-942f-df3c60d522dd"}
    )

    model_config = ConfigDict(from_attributes=True)


class ParentsDelete(BaseModel):
    parent_id: str = Field(
        ...,
        json_schema_extra={"example": "99febb18-8a4c-40b6-942f-df3c60d522dd"}
    )

    model_config = ConfigDict(from_attributes=True)


class CoordinateUpdate(BaseModel):
    street_address: str = Field(
        ...,
        json_schema_extra={"example": "123 Main St"}
    )
    apartment: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Apt 4B"}
    )
    postal_code: str = Field(
        ...,
        json_schema_extra={"example": "12345"}
    )
    city: str = Field(
        ...,
        json_schema_extra={"example": "Anytown"}
    )
    country: str = Field(
        ...,
        json_schema_extra={"example": "USA"}
    )

    model_config = ConfigDict(from_attributes=True)


class EmailPhoneUpdate(BaseModel):
    phone_number: str = Field(
        ...,
        json_schema_extra={"example": "123-456-7890"}
    )
    email: str = Field(
        ...,
        json_schema_extra={"example": "alice@email.com"}
    )

    model_config = ConfigDict(from_attributes=True)


class CoordinateResponse(BaseModel):
    id: str
    street_address: str
    apartment: Optional[str]
    postal_code: str
    city: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class CoordinateUpdateResponse(BaseModel):
    coordinate_id: str
    user_id: str
    street_address: str
    apartment: Optional[str]
    postal_code: str
    city: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class MedicalHistoryResponse(BaseModel):
    id: str
    diagnostic: str
    treatment: str
    doctor: DoctorResponse
    start_date: Optional[date]
    end_date: Optional[date]

    model_config = ConfigDict(from_attributes=True)


class MedicalHistoryUpdateResponse(BaseModel):
    patient_id: str
    history_id: str
    diagnostic: str
    treatment: str
    doctor_id: str
    start_date: Optional[date]
    end_date: Optional[date]

    model_config = ConfigDict(from_attributes=True)


class EstablishmentResponse(BaseModel):
    establishment_id: str
    establishment_name: str
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class MedicalVisitResponse(BaseModel):
    id: str
    patient_id: str
    establishment: EstablishmentResponse
    doctor: DoctorResponse
    visit_date: Optional[date]
    diagnostic_established: Optional[str]
    treatment: Optional[str]
    visit_summary: str
    notes: Optional[str]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class VisitUpdateResponse(BaseModel):
    visit_id: str
    patient_id: str
    establishment_id: str
    doctor_id: str
    visit_date: Optional[date]
    diagnostic: Optional[str]
    treatment: Optional[str]
    summary: str
    notes: Optional[str]
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ParentResponse(BaseModel):
    parent: UserResponse

    model_config = ConfigDict(from_attributes=True)


class PatientResponse(BaseModel):
    medical_insurance_id: str
    gender: str
    city_of_birth: str
    user_id: str
    login: str
    user_type: str
    first_name: str
    last_name: str
    phone_number: str
    email: str
    created_at: datetime
    modified_at: datetime
    date_of_birth: date
    coordinates: List[CoordinateResponse] = []
    medical_history: List[MedicalHistoryResponse] = []
    medical_visits: List[MedicalVisitResponse] = []
    parents: List[ParentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PatientUpdateResponse(BaseModel):
    medical_insurance_id: str
    gender: str
    city_of_birth: str
    user_id: str
    login: str
    user_type: str
    first_name: str
    last_name: str
    phone_number: str
    email: str
    created_at: datetime
    date_of_birth: date

    model_config = ConfigDict(from_attributes=True)


class UserUpdateResponse(BaseModel):
    user_id: str
    login: str
    user_type: str
    first_name: str
    last_name: str
    phone_number: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientCreateResponse(BaseModel):
    user_id: str

    model_config = ConfigDict(from_attributes=True)


class HistoryCreateResponse(BaseModel):
    history_id: str

    model_config = ConfigDict(from_attributes=True)


class CoordinateCreateResponse(BaseModel):
    coordinate_id: str

    model_config = ConfigDict(from_attributes=True)


class VisitCreateResponse(BaseModel):
    visit_id: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(BaseModel):
    user_id: str

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
    patient_id: str

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    error: str

    model_config = ConfigDict(from_attributes=True)


class StatusResponse(BaseModel):
    status: str

    model_config = ConfigDict(from_attributes=True)


class PatientCreate(BaseModel):
    login: str = Field(
        ...,
        json_schema_extra={"example": "johndoe"}
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "mysecretpassword"}
    )
    user_type: str = Field(
        ...,
        # Options: 'ADMIN', 'PATIENT', 'DOCTOR', 'HEALTHCARE PROFESSIONAL'
        json_schema_extra={"example": "PATIENT"}
    )
    first_name: str = Field(
        ...,
        json_schema_extra={"example": "John"}
    )
    last_name: str = Field(
        ...,
        json_schema_extra={"example": "Doe"}
    )
    phone_number: str = Field(
        ...,
        json_schema_extra={"example": "123-456-7890"}
    )
    email: str = Field(
        ...,
        json_schema_extra={"example": "john.doe@example.com"}
    )
    medical_insurance_id: str = Field(
        ...,
        json_schema_extra={"example": "INS123456"}
    )
    gender: str = Field(
        ...,
        json_schema_extra={"example": "Male"}
    )
    city_of_birth: str = Field(
        ...,
        json_schema_extra={"example": "Anytown"}
    )
    date_of_birth: date = Field(
        ...,
        json_schema_extra={"example": "1995-07-15"}
    )
    coordinates: List[CoordinateCreate] = Field(
        ...,
        json_schema_extra={
            "example": [
                {
                    "street_address": "123 Main St",
                    "apartment": "Apt 4B",
                    "postal_code": "12345",
                    "city": "Anytown",
                    "country": "USA"
                },
                {
                    "street_address": "555 Maple Ave",
                    "apartment": "Floor 3",
                    "postal_code": "11223",
                    "city": "Anytown",
                    "country": "USA"
                }
            ]
        }
    )
    parent_ids: Optional[List[str]] = Field(
        None,
        json_schema_extra={"example": [
            "99febb18-8a4c-40b6-942f-df3c60d522dd", "eb711323-52d6-40a8-b335-8b3e587ed009"]}
    )

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    login: str = Field(
        ...,
        json_schema_extra={"example": "johndoe"}
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "mysecretpassword"}
    )
    user_type: str = Field(
        ...,
        # Options: 'ADMIN', 'PATIENT', 'DOCTOR', 'HEALTHCARE PROFESSIONAL'
        json_schema_extra={"example": "PATIENT"}
    )
    first_name: str = Field(
        ...,
        json_schema_extra={"example": "John"}
    )
    last_name: str = Field(
        ...,
        json_schema_extra={"example": "Doe"}
    )
    phone_number: str = Field(
        ...,
        json_schema_extra={"example": "123-456-7890"}
    )
    email: str = Field(
        ...,
        json_schema_extra={"example": "john.doe@example.com"}
    )

    model_config = ConfigDict(from_attributes=True)


class PatientUpdate(BaseModel):
    login: str = Field(
        ...,
        json_schema_extra={"example": "johndoe"}
    )
    gender: str = Field(
        ...,
        json_schema_extra={"example": "Male"}
    )
    city_of_birth: str = Field(
        ...,
        json_schema_extra={"example": "Anytown"}
    )
    date_of_birth: date = Field(
        ...,
        json_schema_extra={"example": "2000-02-20"}
    )
    first_name: str = Field(
        ...,
        json_schema_extra={"example": "John"}
    )
    last_name: str = Field(
        ...,
        json_schema_extra={"example": "Doe"}
    )
    phone_number: str = Field(
        ...,
        json_schema_extra={"example": "123-456-7890"}
    )
    email: str = Field(
        ...,
        json_schema_extra={"example": "john.doe@example.com"}
    )

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    login: str = Field(
        ...,
        json_schema_extra={"example": "johndoe"}
    )
    first_name: str = Field(
        ...,
        json_schema_extra={"example": "John"}
    )
    last_name: str = Field(
        ...,
        json_schema_extra={"example": "Doe"}
    )
    phone_number: str = Field(
        ...,
        json_schema_extra={"example": "123-456-7890"}
    )
    email: str = Field(
        ...,
        json_schema_extra={"example": "john.doe@example.com"}
    )

    model_config = ConfigDict(from_attributes=True)


class CredentialsUpdate(BaseModel):
    login: str = Field(
        ...,
        json_schema_extra={"example": "johndoe"}
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "MySecretPass123"}
    )

    model_config = ConfigDict(from_attributes=True)


class Login(BaseModel):
    email: str = Field(
        ...,
        json_schema_extra={"example": "john.doe@example.com"}
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "secretpassword"}
    )

    model_config = ConfigDict(from_attributes=True)


class DoctorListResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class EstablishmentListResponse(BaseModel):
    establishment_id: str
    establishment_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MFASetupResponse(BaseModel):
    status: str
    secret: Optional[str] = None
    backup_codes: Optional[List[str]] = None
    provisioning_uri: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MFACodeRequest(BaseModel):
    code: str = Field(
        ...,
        json_schema_extra={"example": "123456"}
    )

    model_config = ConfigDict(from_attributes=True)


class MFAStatusResponse(BaseModel):
    status: str
    mfa_configured: bool
    mfa_enabled: bool
    configured_at: Optional[str] = None
    last_modified: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserInfo(BaseModel):
    user_id: str
    user_type: str
    name: str
    medical_insurance_id: Optional[str] = None
    requires_mfa: Optional[bool] = False


class LoginResponse(BaseModel):
    status: str
    token: Optional[str] = None
    temp_token: Optional[str] = None
    user: Optional[UserInfo] = None

    model_config = ConfigDict(from_attributes=True)


class PatientVersionSnapshot(BaseModel):
    """A snapshot of a patient's full record at a specific point in time."""
    user_id: str
    login: str
    user_type: str
    first_name: str
    last_name: str
    phone_number: str
    email: str
    medical_insurance_id: str
    gender: str
    city_of_birth: str
    date_of_birth: date
    created_at: datetime
    modified_at: datetime
    coordinates: List[CoordinateResponse] = []
    medical_history: List[MedicalHistoryResponse] = []
    medical_visits: List[MedicalVisitResponse] = []
    parents: List[ParentResponse] = []
    snapshot_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientVersionHistoryResponse(BaseModel):
    """Response model for patient version history."""
    versions: List[PatientVersionSnapshot]

    model_config = ConfigDict(from_attributes=True)
