import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";

import { createBrowserRouter, RouterProvider } from "react-router";

import App from "./App.tsx";
import Home from "./pages/Home";
import SymptoScan from "./pages/SymptoScan";
import ErrorPage from "./pages/ErrorPage.tsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />, // Parent layout
    children: [
      { index: true, element: <Home /> },
      {
        path: "/origin",
        element: (
          <>
            <main className="container mx-auto py-8 px-4">
              <div className="max-w-4xl mx-auto">
                <SymptoScan />
              </div>
            </main>
          </>
        ),
      },
    ],
    errorElement: <ErrorPage />,
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
