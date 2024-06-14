import logo from './logo.svg';
import './App.css';

import Keycloak from "keycloak-js";

let initOptions = {
  url: 'http://localhost:8080/',
  realm: 'myrealm',
  clientId: 'frontend',
}

let kc = new Keycloak(initOptions);

kc.init({
  onLoad: 'login-required', // Supported values: 'check-sso' (default), 'login-required'
  checkLoginIframe: true
}).then((auth) => {
  if (!auth) {
    window.location.reload();
  }
  else {
    console.log(kc.token)
  }
}, () => {
  /* Notify the user if necessary */
  // alert("Authentication Failed");
});

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
        <br></br>
        <button onClick={() => {kc.logout()}}>Logout</button>
      </header>
    </div>
  );
}

export default App;