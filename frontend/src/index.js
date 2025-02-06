import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import './index.css';
import reportWebVitals from './reportWebVitals';

import Client from './components/client/Client';
import Server from './components/server/Server';
import { ApiProvider } from './components/ApiContext';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Client />,
  },
  {
    path: "/server",
    element: <Server />
  },
]);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ApiProvider>
      <RouterProvider router={router} />
    </ApiProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
