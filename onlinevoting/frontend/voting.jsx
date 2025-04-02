import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './pages/Home';
import Register from './pages/Register';
import Login from './pages/Login';
import Vote from './pages/Vote';
import Admin from './pages/Admin';

function App() {
    return (
        <Router>
            <div className="App">
                <Switch>
                    <Route path="/" exact component={Home} />
                    <Route path="/register" component={Register} />
                    <Route path="/login" component={Login} />
                    <Route path="/vote" component={Vote} />
                    <Route path="/admin" component={Admin} />
                </Switch>
            </div>
        </Router>
    );
}

export default App;