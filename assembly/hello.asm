; Linux x86-64 / NASM
; Hello, World! via sys_write / sys_exit

section .data
    msg db "Hello, World!", 10
    len equ $ - msg

section .text
    global _start

_start:
    ; write(1, msg, len)
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg
    mov rdx, len
    syscall

    ; exit(0)
    mov rax, 60         ; sys_exit
    xor rdi, rdi
    syscall
