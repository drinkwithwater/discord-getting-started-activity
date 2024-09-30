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
  let ret = await discordSdk.commands.authorize({
    client_id:discordSdk.clientId,
    response_type:"code",
    state: "",
    scope:[
      "identify"
    ],
  });
  console.log("code:"+ret.code);
}

setupDiscordSdk().then(() => {
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