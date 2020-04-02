import React, { Fragment } from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import { ApolloProvider } from "@apollo/react-hooks";

import client from "../graphql";
import CommissionList from "./commission/CommissionList";
import CommissionForm from "./commission/CommissionForm";

import { registerLocale, setDefaultLocale } from "react-datepicker";
import pl from "date-fns/locale/pl";

registerLocale("pl", pl);
setDefaultLocale("pl");

function App() {
    return (
        <ApolloProvider client={client}>
            <BrowserRouter>
                <div className="content">
                    <Switch>
                        <Route exact path="/tiles" component={CommissionList} />
                        <Route exact path="/tiles/zlecenia/nowe" component={CommissionForm} />
                        <Route path="/tiles/zlecenia/:id" component={CommissionForm} />
                    </Switch>
                </div>
            </BrowserRouter>
        </ApolloProvider>
    );
}

ReactDOM.render(<App />, document.getElementById("app"));

export default App;
