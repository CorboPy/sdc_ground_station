# Initial commit

# CLIENT PROCESSES
# 1. Default. User input() OR menu system for messages to server. Starts 2 once message is sent. Time wait before can send next message? Can only send one request at a time
# 2. Listening for recieved messages and distributing to other processes below. If "TCAM stream" json, send to 3. If "data snapshot" json, send to 4.
# 3. Plot TCAM data from recieved json string
# 4. Parse recieved data or snapshot of TCAM to determine evacuation areas. For TCAM snapshot, need to write a .txt with columns "location", "temp", "safe or evacuate?" for all locations

# SERVER PROCESSES
# 1. Default. Waits for connection from client. If it's a command, start process 2. If data req, start process 3. If live TCAM stream (TRUE), start process 4. If live TCAM stream (FALSE), safely end process 4. If shutdown, run shutdown function on this process, ensuring other processes are shut down safely.
# 2. Command specific process function
# 3. Data request function
# 4. Live TCAM stream function

# https://www.youtube.com/watch?v=79dlpK03t30&list=PLGs0VKk2DiYxdMjCJmcP6jt4Yw6OHK85O&index=48