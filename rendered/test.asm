; Generated using lippy!
extern     _printf    ; Generated by lippy assembler
extern     _scanf     ; Generated by lippy assembler
%macro print 1
        push    %1
        call    _printf
        add     esp, 4
%endmacro
section .data
    lippy_version        db    "Lippy 0.0.0.1", 0x0A, 0 ; Generated by lippy assembler
section .text
    global _main  ; this is the entry point for the linker
    _main:
        print                lippy_version       ; Generated by lippy assembler
        mov                  eax, 0              ; Generated by lippy assembler
        ret                                      ; Generated by lippy assembler

