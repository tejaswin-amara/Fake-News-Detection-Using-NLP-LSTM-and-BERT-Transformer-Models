import http from "k6/http";
import { check } from "k6";

const target = (__ENV.K6_TARGET_URL || "").replace(/\/+$/, "");
const authorised = __ENV.K6_AUTHORIZE_TARGET === "yes";

if (!target || !/^https?:\/\/[^\s]+$/i.test(target)) {
  throw new Error("K6_TARGET_URL must be an explicit http(s) endpoint");
}

if (!authorised) {
  throw new Error("Set K6_AUTHORIZE_TARGET=yes only after reviewing target ownership, capacity, and consent");
}

export const options = {
  scenarios: {
    metadata_only_smoke: {
      executor: "shared-iterations",
      vus: 1,
      iterations: 3,
      maxDuration: "30s",
      gracefulStop: "5s",
    },
  },
  thresholds: {
    checks: ["rate==1"],
    http_req_failed: ["rate==0"],
    http_req_duration: ["p(95)<3000"],
  },
};

export default function () {
  const payload = JSON.stringify({
    title: "synthetic performance fixture",
    text: "synthetic bounded classification input",
  });
  const response = http.post(`${target}/predict`, payload, {
    headers: { "Content-Type": "application/json" },
    tags: { profile: "metadata_only_smoke" },
  });
  check(response, {
    "predict returns 200": (result) => result.status === 200,
    "predict returns JSON": (result) => (result.headers["Content-Type"] || "").includes("application/json"),
  });
}
