export PYTHONSTARTUP=repl.py
export PYTHONPATH=/app

alias ll='ls -lA'



if [ -d venv ]; then
    . venv/bin/activate
fi

