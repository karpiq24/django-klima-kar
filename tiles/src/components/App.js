import React, { Fragment } from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import { ApolloProvider } from "@apollo/react-hooks";

import client from "../graphql";
import CommissionList from "./commission/CommissionList";

function App() {
    return (
        <ApolloProvider client={client}>
            <BrowserRouter>
                <div className="content">
                    <Switch>
                        <Route exact path="/tiles" component={CommissionList} />
                    </Switch>
                </div>
            </BrowserRouter>
        </ApolloProvider>
    );
}

ReactDOM.render(<App />, document.getElementById("app"));

export default App;
