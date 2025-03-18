import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Link } from "react-router";

export default function ErrorPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-gray-100 p-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="text-center bg-white p-10 rounded-2xl shadow-lg"
      >
        <h1 className="text-6xl font-bold text-red-500">404</h1>
        <p className="text-lg text-gray-600 mt-4">
          Oops! The page you're looking for doesn't exist.
        </p>

        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="mt-6"
        >
          <Button asChild>
            <Link to="/">Go Home</Link>
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
}
