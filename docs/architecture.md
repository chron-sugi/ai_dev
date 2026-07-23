
Workflow


Research -> Propose -> Deliberate -> Decide -> Architect -> Plan -> Code -> Review -> Test

## REQUEST
- User Initiates request
- AI generates .velocai/tasks/<task-id>


## Researcher
- Optional 
- Dependent on ask
- Domain specific concerns require research doc. 



**Artifacts**
- docs/<domain>
- RESEARCH.md



## EXPLORER
- Ezplores codebase for prior art

**Artifact**
- Generates exploration note or escalates to architect


## PROPOSE

**Artifacts**
- PROPOSALS.md

## DELIBERATE



## DECIDE
**Artifacts**
<.velocai>

## Create ADR - Escalation Path

**Artifacts**
docs/adrs/adr-xxxx-<descriptive name>


## Create Contract
- Create domain contract
**Inputs**
- create-domain-contract prompt
- 

**Paths**
1. Create complete domain contract 
2. Create partial domain contract with unresolved gaps
- If 2, revise ADR and re-run create-domain contract prompt

**Artifacts***
.velocai/tasks/<task-id>/CONTRACT.yaml

## PLAN

### PLAN REVIEW

## CODE 