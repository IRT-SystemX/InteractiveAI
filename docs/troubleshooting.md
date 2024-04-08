
# Troubleshooting

Are you having issues with setting up your environment? Here are some tips that might help.

## EoL Sequence Configuration errors.

Some users may encounter issues if their system is automatically converting end of line sequence from LF to CRLF.
If the problem is related to git configuration, [here is a link that can help. ](https://medium.com/@csmunuku/windows-and-linux-eol-sequence-configure-vs-code-and-git-37be98ef71df)


## Always unauthorized

Sometimes we have issues setting up .env file with the correct value.
The .env should contain:

```env
HOST_IP=<IP_Address>
```

If the IP_Address is not your network IP address, please set it manually and run the system using native docker-compose commands.

> **_NOTE:_** You are welcome to contribute with any issue that you encounter during setup.