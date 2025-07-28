
# Troubleshooting

Are you having issues with setting up your environment? Here are some tips that might help.

## Ports already in use

InteractiveAI uses about twenty ports on server. If a port needed for InteractiveAI is already in use, InteractiveAI will fail (with messages in logs but the can be missed).
The script `resources/checkPorts.sh` tests the availability of each port specified in `config/dev/cab-standalone/docker-compose.yml` and write a diagnosis on console.

It it succeeds:
```
brettevi@PCAlien:~/Projets/InteractiveAI$ ./resources/checkPorts.sh
Ports used for InteractiveAI: 89 3200 5000 5100 5200 5400 5433 5434 5436 5437 5438 5500 12002 12100 12102 12103 12104 27017
All is fine: all ports used by InteractiveAI are available
```

If it fails:
```
brettevi@PCAlien:~/Projets/InteractiveAI$ ./resources/checkPorts.sh
Ports used for InteractiveAI: 89 3200 5000 5100 5200 5400 5433 5434 5436 5437 5438 5500 12002 12100 12102 12103 12104 27017
docker: Error response from daemon: driver failed programming external connectivity on endpoint stoic_williams (b69f8285b2ec63145267ad7ea04969cf58dc423528729c7c3f07b5d5c3ccc342): Bind for 0.0.0.0:89 failed: port is already allocated.
...
docker: Error response from daemon: driver failed programming external connectivity on endpoint zen_feistel (f3047f6ae4ebf5e78dc034137d24a832e2ff60490424ba8ba4ae2531d2222142): Bind for 0.0.0.0:12104 failed: port is already allocated.
docker: Error response from daemon: driver failed programming external connectivity on endpoint keen_swanson (82f2ac17d11057767379dc0f492b5a9b8fd7620fb562e8107e9ce1453e548052): Bind for 0.0.0.0:27017 failed: port is already allocated.
Check your counfiguration: 18 port(s) used by InteractiveAI are already used
InteractiveAI can't run on this platform with this /home/brettevi/Projets/InteractiveAI/config/dev/cab-standalone/docker-compose.yml ports configuration
```

This command may also be used with a specific docker-compose.yml file. For example, to test Powergrid simulator ports availability, one can use:
```
brettevi@PCAlien:~/Projets/InteractiveAI$ ./resources/checkPorts.sh usecases_examples/PowerGrid/docker-compose.yml
Ports used for InteractiveAI: 5150
docker: Error response from daemon: driver failed programming external connectivity on endpoint funny_rhodes (6291f43617a7798a833fdeee05c32c75c2d0bf765eac5dc3b8fe08b7255e57a1): Bind for 0.0.0.0:5150 failed: port is already allocated.
Check your counfiguration: 1 port(s) used by InteractiveAI are already used
InteractiveAI can't run on this platform with this usecases_examples/PowerGrid/docker-compose.yml ports configuration
```

## EoL Sequence Configuration errors.

Some users may encounter issues if their system is automatically converting end of line sequence from LF to CRLF.
If the problem is related to git configuration, [here is a link that can help. ](https://medium.com/@csmunuku/windows-and-linux-eol-sequence-configure-vs-code-and-git-37be98ef71df)


## Always unauthorized

Sometimes we have issues setting up .env file with the correct value.
The .env should contain:

```env
HOST_IP=<IP_Address>
```

If the IP_Address is not your network IP address, please set it manually and run the system using native docker compose commands.

> **_NOTE:_** You are welcome to contribute with any issue that you encounter during setup.