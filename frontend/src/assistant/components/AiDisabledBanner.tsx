import Link from "next/link";
import { SparklesIcon } from "@heroicons/react/24/outline";

const AiDisabledBanner = () => {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-4 rounded-2xl bg-white p-10 text-center shadow-md">
        <div className="flex rounded-full bg-amber-100 p-4">
          <SparklesIcon className="h-8 w-8 text-amber-600" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            AI features are not enabled
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Enable AI features in your account settings to use the assistant.
          </p>
        </div>
        <Link
          href="/user/account"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Go to account settings
        </Link>
      </div>
    </div>
  )
}

export default AiDisabledBanner;
