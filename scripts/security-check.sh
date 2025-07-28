# scripts/security-check.sh - Script de verificación integral de seguridad
#!/bin/bash
set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Contadores
ISSUES_FOUND=0
TOTAL_CHECKS=0

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
    ((ISSUES_FOUND++))
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
    ((ISSUES_FOUND++))
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO: $1${NC}"
}

check_step() {
    ((TOTAL_CHECKS++))
    echo -e "${BLUE}[CHECK $TOTAL_CHECKS] $1${NC}"
}

# Verificar herramientas de seguridad
check_security_tools() {
    check_step "Checking security tools availability"
    
    tools=("bandit" "safety" "semgrep" "flake8")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            log "$tool is available"
        else
            error "$tool is not installed"
        fi
    done
}

# Análisis estático con Bandit
run_bandit_scan() {
    check_step "Running Bandit security scan"
    
    if command -v bandit &> /dev/null; then
        log "Starting Bandit scan..."
        
        # Crear directorio de reportes si no existe
        mkdir -p security_reports
        
        # Ejecutar Bandit
        if bandit -r . -c .bandit -f json -o security_reports/bandit-report.json 2>/dev/null; then
            log "Bandit scan completed successfully"
            
            # Verificar si hay issues críticos
            if command -v jq &> /dev/null; then
                high_issues=$(jq '.results[] | select(.issue_severity == "HIGH") | length' security_reports/bandit-report.json 2>/dev/null | wc -l)
                medium_issues=$(jq '.results[] | select(.issue_severity == "MEDIUM") | length' security_reports/bandit-report.json 2>/dev/null | wc -l)
                
                if [[ $high_issues -gt 0 ]]; then
                    error "Found $high_issues HIGH severity security issues"
                fi
                
                if [[ $medium_issues -gt 0 ]]; then
                    warn "Found $medium_issues MEDIUM severity security issues"
                fi
            fi
            
            # Mostrar resumen en texto
            bandit -r . -c .bandit -f txt | tail -10
        else
            error "Bandit scan failed"
        fi
    else
        error "Bandit not available"
    fi
}

# Verificación de dependencias vulnerables
check_vulnerable_dependencies() {
    check_step "Checking for vulnerable dependencies"
    
    if command -v safety &> /dev/null; then
        log "Running Safety check..."
        
        if safety check --json --output security_reports/safety-report.json 2>/dev/null; then
            log "No vulnerable dependencies found"
        else
            warn "Potential vulnerable dependencies detected"
            # Mostrar issues sin parar el script
            safety check || true
        fi
    else
        error "Safety tool not available"
    fi
}

# Análisis con Semgrep
run_semgrep_scan() {
    check_step "Running Semgrep security analysis"
    
    if command -v semgrep &> /dev/null; then
        log "Starting Semgrep scan..."
        
        # Usar reglas de seguridad específicas
        if semgrep --config=auto --json --output=security_reports/semgrep-report.json . 2>/dev/null; then
            log "Semgrep scan completed"
            
            # Contar findings
            if command -v jq &> /dev/null; then
                findings=$(jq '.results | length' security_reports/semgrep-report.json 2>/dev/null || echo "0")
                if [[ $findings -gt 0 ]]; then
                    warn "Semgrep found $findings potential security issues"
                else
                    log "No security issues found by Semgrep"
                fi
            fi
        else
            warn "Semgrep scan completed with warnings"
        fi
    else
        info "Semgrep not available (optional)"
    fi
}

# Verificar configuraciones de seguridad en el código
check_security_configurations() {
    check_step "Checking security configurations in code"
    
    # Verificar SSL verification
    if grep -r "verify.*=.*False" . --exclude-dir=.git --exclude-dir=venv --exclude-dir=.venv; then
        warn "Found SSL verification disabled in code"
    else
        log "SSL verification appears to be properly configured"
    fi
    
    # Verificar hardcoded secrets
    secret_patterns=(
        "password.*=.*['\"][^'\"]*['\"]"
        "api_key.*=.*['\"][^'\"]*['\"]"
        "secret.*=.*['\"][^'\"]*['\"]"
        "token.*=.*['\"][^'\"]*['\"]"
    )
    
    for pattern in "${secret_patterns[@]}"; do
        if grep -ri "$pattern" . --exclude-dir=.git --exclude-dir=venv --exclude-dir=.venv --exclude-dir=tests; then
            warn "Potential hardcoded secret found: $pattern"
        fi
    done
    
    # Verificar imports inseguros
    insecure_imports=(
        "import pickle"
        "import subprocess"
        "import os"
        "exec("
        "eval("
    )
    
    for import in "${insecure_imports[@]}"; do
        matches=$(grep -r "$import" . --exclude-dir=.git --exclude-dir=venv --exclude-dir=.venv --exclude-dir=tests | wc -l)
        if [[ $matches -gt 0 ]]; then
            info "Found $matches uses of potentially dangerous: $import (review required)"
        fi
    done
}

# Verificar permisos de archivos
check_file_permissions() {
    check_step "Checking file permissions"
    
    # Verificar archivos ejecutables
    executable_files=$(find . -type f -executable -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*")
    
    if [[ -n "$executable_files" ]]; then
        info "Executable files found:"
        echo "$executable_files"
    fi
    
    # Verificar archivos con permisos excesivos
    if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "cygwin" ]]; then
        world_writable=$(find . -type f -perm -002 -not -path "./.git/*" -not -path "./venv/*")
        if [[ -n "$world_writable" ]]; then
            warn "World-writable files found:"
            echo "$world_writable"
        else
            log "No world-writable files found"
        fi
    fi
}

# Verificar configuración de Docker si existe
check_docker_security() {
    check_step "Checking Docker security (if applicable)"
    
    if [[ -f "Dockerfile" ]]; then
        info "Dockerfile found, checking security..."
        
        # Verificar si se ejecuta como root
        if grep -q "USER root" Dockerfile; then
            warn "Dockerfile runs as root user"
        fi
        
        # Verificar si se usan imágenes oficiales
        if grep -q "FROM.*:latest" Dockerfile; then
            warn "Dockerfile uses :latest tag (not recommended for production)"
        fi
        
        # Verificar exposición de puertos
        exposed_ports=$(grep "EXPOSE" Dockerfile | wc -l)
        if [[ $exposed_ports -gt 0 ]]; then
            info "Dockerfile exposes $exposed_ports port(s)"
        fi
    else
        info "No Dockerfile found"
    fi
}

# Generar reporte final
generate_security_report() {
    check_step "Generating security report"
    
    mkdir -p security_reports
    
    report_file="security_reports/security-summary-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Security Analysis Report

**Generated:** $(date)
**Project:** Badg3rFuzz Security Tool

## Summary

- **Total Checks:** $TOTAL_CHECKS
- **Issues Found:** $ISSUES_FOUND
- **Status:** $(if [[ $ISSUES_FOUND -eq 0 ]]; then echo "✅ PASSED"; else echo "⚠️  REVIEW REQUIRED"; fi)

## Checks Performed

1. ✓ Security tools availability
2. ✓ Static code analysis (Bandit)
3. ✓ Dependency vulnerability scan (Safety)
4. ✓ Advanced security analysis (Semgrep)
5. ✓ Security configuration review
6. ✓ File permissions audit
7. ✓ Docker security check

## Recommendations

$(if [[ $ISSUES_FOUND -gt 0 ]]; then
    echo "- Review and address the $ISSUES_FOUND security issues found"
    echo "- Check detailed reports in security_reports/ directory"
    echo "- Run security tests regularly in CI/CD pipeline"
else
    echo "- No security issues detected in automated scan"
    echo "- Continue following security best practices"
    echo "- Regular security reviews recommended"
fi)

## Files Generated

- \`bandit-report.json\` - Static analysis results
- \`safety-report.json\` - Dependency vulnerability scan
- \`semgrep-report.json\` - Advanced security analysis

---
*Generated by Badg3rFuzz Security Check v1.0*
EOF

    log "Security report generated: $report_file"
}

# Función principal
main() {
    log "🔒 Starting comprehensive security check for Badg3rFuzz..."
    echo
    
    check_security_tools
    run_bandit_scan
    check_vulnerable_dependencies
    run_semgrep_scan
    check_security_configurations
    check_file_permissions
    check_docker_security
    generate_security_report
    
    echo
    if [[ $ISSUES_FOUND -eq 0 ]]; then
        log "✅ Security check completed successfully! No issues found."
        exit 0
    else
        warn "⚠️  Security check completed with $ISSUES_FOUND issues found."
        warn "Please review the detailed reports in security_reports/ directory"
        exit 1
    fi
}

# Ejecutar si es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi