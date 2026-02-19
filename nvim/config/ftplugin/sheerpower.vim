" Vim ftplugin for SheerPower 4GL
" Language: SheerPower 4GL
" Filenames: *.spsrc, *.spinc

if exists("b:did_ftplugin")
  finish
endif
let b:did_ftplugin = 1

" ── Comment format ───────────────────────────────────────────────────────────
" Use ! for single-line comments (gc / Commentary plugin)
setlocal commentstring=!\ %s
setlocal comments=:!,://

" ── Indentation ──────────────────────────────────────────────────────────────
setlocal expandtab
setlocal shiftwidth=2
setlocal softtabstop=2
setlocal tabstop=2

" ── Text width ───────────────────────────────────────────────────────────────
setlocal textwidth=120

" ── Folding: fold on block keywords ─────────────────────────────────────────
setlocal foldmethod=indent

" ── Restore settings on filetype change ─────────────────────────────────────
let b:undo_ftplugin = "setlocal commentstring< comments< expandtab< shiftwidth< softtabstop< tabstop< textwidth< foldmethod<"
