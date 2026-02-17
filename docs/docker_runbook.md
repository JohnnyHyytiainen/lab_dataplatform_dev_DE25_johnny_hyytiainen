# "Runbook" (playbook). My easy go to commands in mini-format and runbook for replicating this repo and docker container.

## Here are the needed commands to handle my PostgreSQL container for this project.

### **Start and run commands:**
- Start the environment with: 
    - `docker-compose up -d`

- Check the status with:  
    - `docker-compose ps`  

- Run the python script to fill DB with data:
    - `python src/products_lab_v2.py`

**NOTE: IMPORTANT TO RUN ON PORT 5434, if not you can change it easily in the compose.yml file**

- Close (Saves the data)
    - `docker-compose down`

---

### **Error handling and logs:**
- If the python script complains on 'connection refused' and gives errors check this first:
    - `docker-compose logs -f`
    - See what the database is doing.
    - Press `ctrl+c` to exit

---

### **If you want to jump in to the container and run queries without PgAdmin4:** 
- If you want to jump in to the container and run it to query without using PgAdmin4 GUI use this command:

    - `docker exec -it lab_postgres_container psql -U postgres -d lab_db`

    - To Exit write:  `\q`

--- 

### **Panic commands (Nuke and reset):**
- Use these commands if you want to start over from scratch.  
**NOTE: This REMOVES ALL DATA IN DATABASE**

- Shut down and remove the Volume:
    - `docker-compose down -v`

- Start up again (new and empty DB):
    - `docker-compose up -d`

- Run the python script again to fill DB with data:
    - `python src/products_lab_v2.py`




