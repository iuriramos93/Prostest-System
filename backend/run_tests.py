#!/usr/bin/env python
"""
Script para executar os testes do Sistema de Protesto

Este script facilita a execução dos testes do backend do Sistema de Protesto.
Permite executar todos os testes ou grupos específicos de testes.
"""

import os
import sys
import subprocess

def print_header(message):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80 + "\n")

def run_tests(args=None):
    """Executa os testes com os argumentos fornecidos"""
    cmd = [sys.executable, "-m", "pytest"]
    if args:
        cmd.extend(args)
    
    print(f"Executando comando: {' '.join(cmd)}")
    return subprocess.call(cmd)

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Se argumentos foram fornecidos, passa-os diretamente para o pytest
        return run_tests(sys.argv[1:])
    
    print_header("Sistema de Protesto - Testes do Backend")
    print("Escolha uma opção de teste:")
    print("1. Executar todos os testes")
    print("2. Executar testes de autenticação")
    print("3. Executar testes de títulos")
    print("4. Executar testes de remessas")
    print("5. Executar testes de desistências")
    print("6. Executar testes de erros")
    print("7. Executar testes de relatórios")
    print("8. Executar testes de modelos")
    print("9. Executar testes com cobertura detalhada")
    print("0. Sair")
    
    choice = input("\nDigite o número da opção desejada: ")
    
    if choice == "1":
        print_header("Executando todos os testes")
        return run_tests()
    elif choice == "2":
        print_header("Executando testes de autenticação")
        return run_tests(["tests/test_auth.py", "-v"])
    elif choice == "3":
        print_header("Executando testes de títulos")
        return run_tests(["tests/test_titulos.py", "-v"])
    elif choice == "4":
        print_header("Executando testes de remessas")
        return run_tests(["tests/test_remessas.py", "-v"])
    elif choice == "5":
        print_header("Executando testes de desistências")
        return run_tests(["tests/test_desistencias.py", "-v"])
    elif choice == "6":
        print_header("Executando testes de erros")
        return run_tests(["tests/test_erros.py", "-v"])
    elif choice == "7":
        print_header("Executando testes de relatórios")
        return run_tests(["tests/test_relatorios.py", "-v"])
    elif choice == "8":
        print_header("Executando testes de modelos")
        return run_tests(["tests/test_models.py", "-v"])
    elif choice == "9":
        print_header("Executando testes com cobertura detalhada")
        return run_tests(["--cov=app", "--cov-report=html", "--cov-report=term"])
    elif choice == "0":
        print("Saindo...")
        return 0
    else:
        print("Opção inválida!")
        return 1

if __name__ == "__main__":
    sys.exit(main())