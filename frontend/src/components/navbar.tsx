import { useState } from "react";
import { Link, NavLink } from "react-router";
import { motion } from "framer-motion";
import { Menu, X, Home as HomeIcon, Stethoscope } from "lucide-react";
import { Button } from "@/components/ui/button";

import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
} from "@clerk/clerk-react";

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 md:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2"
        >
          <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold">HV</span>
          </div>
          <Link to="/" className="text-xl font-bold text-primary">
            HealthVitals AI
          </Link>
        </motion.div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex items-center gap-6"
          >
            <NavLink to="/" className={({isActive}) => `text-sm font-medium flex items-center gap-1 ${isActive ? "text-primary" : "hover:text-primary"}`}>
              <HomeIcon className="h-4 w-4" /> Home
            </NavLink>
            <NavLink to="/symptoscan-pro" className={({isActive}) => `text-sm font-medium flex items-center gap-1 ${isActive ? "text-primary" : "hover:text-primary"}`}>
              <Stethoscope className="h-4 w-4" /> SymptomScan Pro
            </NavLink>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex items-center gap-2"
          >
            <SignedOut>
              <SignInButton mode="modal">
                <Button variant="outline" className="text-primary px-4 py-2">
                  Sign In
                </Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </motion.div>
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle menu"
        >
          {isMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
          className="md:hidden border-t"
        >
          <div className="container mx-auto px-4 py-4 flex flex-col gap-4">
            <NavLink
              to="/"
              className={({isActive}) => `py-2 text-sm font-medium flex items-center gap-1 ${isActive ? "text-primary" : "hover:text-primary"}`}
              onClick={() => setIsMenuOpen(false)}
            >
              <HomeIcon className="h-4 w-4" /> Home
            </NavLink>
            <NavLink
              to="/symptoscan-pro"
              className={({isActive}) => `py-2 text-sm font-medium flex items-center gap-1 ${isActive ? "text-primary" : "hover:text-primary"}`}
              onClick={() => setIsMenuOpen(false)}
            >
              <Stethoscope className="h-4 w-4" /> SymptomScan Pro
            </NavLink>
            <div className="flex flex-col gap-2 pt-2 border-t">
              <SignedOut>
                <SignInButton mode="modal">
                  <Button variant="outline" className="w-full justify-center">
                    Sign In
                  </Button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </motion.div>
      )}
    </header>
  );
}
