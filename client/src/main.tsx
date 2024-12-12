// Import the SDK
import React from "react";
import ReactDOM from "react-dom/client";
import { DiscordSDK } from "@discord/embedded-app-sdk";

import "./main.css";
import rocketLogo from '/rocket.png';

// Instantiate the SDK
let discordSdk:DiscordSDK = null;

async function setupDiscordSdk() {
  discordSdk = new DiscordSDK("1283000047155544066")
  await discordSdk.ready();
  console.log(discordSdk.guildId, discordSdk.channelId, discordSdk.clientId)
  let ret = await discordSdk.commands.authorize({
    client_id:discordSdk.clientId,
    response_type:"code",
    state: "",
    prompt:"none",
    scope:[
      "identify",
      "guilds.members.read",
      "guilds",
      "applications.commands",
    ],
  });
  const response = await fetch(".proxy/discord/discord_auth", {
    method:"POST",
    body:JSON.stringify({
      code:ret.code,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
  console.log("response", response)
  const authResult = await response.json() as {
    access_token:string
  };
  console.log("authResult", authResult)
  const auth2 = await discordSdk.commands.authenticate({
    access_token:authResult.access_token,
  });
  console.log("auth2", auth2)
}

setupDiscordSdk().then(()=>{
  console.log("Discord SDK is ready");
});


ReactDOM.createRoot(document.getElementById('app')).render(
  <React.StrictMode>
    <div>
      <img src={rocketLogo} className="logo" alt="Discord" />
      <h1>Hello, World!</h1>
    </div>
  </React.StrictMode>
)
