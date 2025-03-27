import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import {
  ClerkProvider,
  RedirectToSignIn,
  SignedIn,
  SignedOut,
} from "@clerk/clerk-react";

import "./index.css";

import { createBrowserRouter, RouterProvider } from "react-router";

import App from "./App.tsx";
import Home from "./pages/Home";
import SymptoScan from "./pages/SymptoScan";
import ErrorPage from "./pages/ErrorPage.tsx";
import PageWrapper from "./components/page-motion-fade.tsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />, // Parent layout
    children: [
      { index: true, element: <Home /> },
      {
        path: "/symptoscan-pro",
        element: (
          <>
            <SignedIn>
              <PageWrapper>
                <main className="container mx-auto py-8 px-4">
                  <div className="max-w-4xl mx-auto">
                    <SymptoScan isPro={true} />
                  </div>
                </main>
              </PageWrapper>
            </SignedIn>
            <SignedOut>
              <RedirectToSignIn />
            </SignedOut>
          </>
        ),
      },
    ],
    errorElement: <ErrorPage />,
  },
]);

const clerkFrontendApi = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || "";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ClerkProvider publishableKey={clerkFrontendApi} afterSignOutUrl="/">
      <RouterProvider router={router} />
    </ClerkProvider>
  </StrictMode>
);
