#!/usr/bin/env bash
# Wrapper скрипт для проверки сообщения коммита через Commitizen
# Используется в pre-commit hook commit-msg
#
# Pre-commit передает путь к файлу сообщения коммита как первый аргумент ($1)
# Этот скрипт передает его в cz check --commit-msg-file

if [ -z "$1" ]; then
    echo "Ошибка: не указан файл сообщения коммита" >&2
    exit 1
fi

# Вызываем commitizen check с файлом сообщения коммита
cz check --commit-msg-file "$1"
