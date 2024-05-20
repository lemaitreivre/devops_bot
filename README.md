# devops_bot
devops bot for pt_start  

fill secrets.yml by yourself

postgresql-14

start : ansible-playbook -i inventory/hosts --extra-vars "@secrets.yml" playbook_tg_bot.yml
