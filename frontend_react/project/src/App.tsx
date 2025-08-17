import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Github, Globe, Loader2, XCircle, Rocket, Code2 } from "lucide-react";
import axios from "axios";

interface DeploymentResponse {
  message: string;
  deployment_id: string;
  container_id: string;
  ngrok_url: string;
  image_id: string;
  repo_path:string;
  ngrok_pid:string;
}

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [deploymentData, setDeploymentData] =
    useState<DeploymentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    // Retrieve deploymentData from localStorage on page load
    const storedDeploymentData = localStorage.getItem("deploymentData");
    if (storedDeploymentData) {
      setDeploymentData(JSON.parse(storedDeploymentData));
    }
  }, []);


  const handleDeploy = async (e: React.FormEvent) => {
    e.preventDefault(); //prevents the page from reloading when the form is submitted.
    setIsLoading(true); //deployment process has started, so a loading indicator (if present in the UI) will be shown.
    setError(null); //Resets any previous errors before making the request.

    try {
      const response = await axios.post( //The await keyword ensures that the function waits for the API response before proceeding.
        " http://127.0.0.1:8000/api/deploy_repo/", //Sends a POST request to http://127.0.0.1:8000/api/deploy_repo/ using axios
        { repo_url: repoUrl } // meaning it sends the repository URL entered by the user.
      );
      setDeploymentData(response.data);//If the API request is successful, the response data (which is expected to follow the DeploymentResponse format) is stored in the deploymentData state
      
    } catch (err : any) {
      // setError(
      //   "Deployment failed. Please check your repository URL and try again."
      // );
      if (axios.isAxiosError(err)) {
        if (err.response) {
          // Server responded with an error status code
          setError(err.response.data?.error || "Deployment failed. Please check your repository URL and try again.");
        } else if (err.request) {
          // Request was sent but no response received (server down, network issue)
          setError("No response from the server. Please check your network connection.");
        } else {
          // Other unexpected Axios error
          setError("An unexpected error occurred. Please try again.");
        }
      } else {
        // Non-Axios error (e.g., JavaScript runtime error)
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setIsLoading(false); //Whether the request succeeds or fails, setIsLoading(false); is executed to stop the loading state.
    }
  };

  const handleStopDeployment = async () => { //This is an asynchronous function that will be called when the user wants to stop the deployment.
    if (!deploymentData?.container_id || !deploymentData?.image_id ) return;

    try {
      await axios.post(" http://127.0.0.1:8000/api/deploy_repo/stop/", {
        container_id: deploymentData.container_id,
        image_id: deploymentData.image_id,
        repo_path:deploymentData.repo_path,
        ngrok_pid:deploymentData.ngrok_pid,
      });
      setDeploymentData(null); //After successfully stopping the deployment: Clears deployment information.
      setRepoUrl("");//Resets the repository URL.
      localStorage.removeItem("deploymentData");
      alert("Deployment stopped successfully!");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || "Failed to stop deployment. Please try again.");
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    }
  };
  useEffect(() => {
    const handleBeforeUnload = async (event: { preventDefault: () => void; returnValue: string; }) => {
      event.preventDefault();
      if (deploymentData) {
        await handleStopDeployment();
        event.returnValue = "Are you sure you want to leave?";
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [deploymentData]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white">
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Rocket className="w-12 h-12" />
            <h1 className="text-5xl font-bold">HostYourProject</h1>
          </div>
          <p className="text-xl text-gray-300">
            Deploy your GitHub projects with ease
          </p>
        </motion.div>

        <div className="max-w-2xl mx-auto">
          <motion.form
            onSubmit={handleDeploy}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-8 shadow-2xl"
          >
            <div className="flex gap-4 mb-6">
              <div className="flex-1">
                <label className="block text-sm font-medium mb-2">
                  GitHub Repository URL
                </label>
                <div className="relative">
                  <Github className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)} //is an event handler for an input field. It updates the state (repoUrl) whenever the user types something in the input box
                    placeholder="https://github.com/username/repo"
                    className="w-full pl-10 pr-4 py-3 bg-white/5 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
                    required
                  />
                </div>
              </div>
            </div>

            {/* <div className="flex justify-center gap-4">
              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg font-medium disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Code2 className="w-5 h-5" />
                    Deploy Project
                  </>
                )}
              </motion.button>

              {deploymentData && (
                <motion.button
                  type="button"
                  onClick={handleStopDeployment}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-6 py-3 bg-red-500/80 rounded-lg font-medium"
                >
                  <XCircle className="w-5 h-5" />
                  Stop Deployment
                </motion.button>
              )}
            </div> */}
            <div className="flex justify-center gap-4">
              {deploymentData ? (
                // Stop Deployment Button (Shown When Deployment is Active)
                <motion.button
                  type="button"
                  onClick={handleStopDeployment}
                  disabled={isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-6 py-3 bg-red-500 rounded-lg font-medium disabled:opacity-50"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <XCircle className="w-5 h-5" />
                      Stop Deployment
                    </>
                  )}
                </motion.button>
              ) : (
                // Deploy Project Button (Shown When No Deployment is Active)
                <motion.button
                  type="submit"
                  disabled={isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg font-medium disabled:opacity-50"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Code2 className="w-5 h-5" />
                      Deploy Project
                    </>
                  )}
                </motion.button>
              )}
            </div>

          </motion.form>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="mt-6 p-4 bg-red-500/20 rounded-lg text-center"
              >
                {error}
              </motion.div>
            )}

            {deploymentData && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="mt-8 bg-white/10 backdrop-blur-lg rounded-xl p-6"
              >
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Globe className="w-5 h-5" />
                  Deployment Success!
                </h3>
                <div className="space-y-3">
                  <p className="text-gray-300">
                    Your project is live at:{" "}
                    <a
                      href={deploymentData.ngrok_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-400 hover:text-purple-300 underline"
                    >
                      {deploymentData.ngrok_url}
                    </a>
                  </p>
                  <p className="text-sm text-gray-400">
                    Deployment ID: {deploymentData.deployment_id}
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default App;
