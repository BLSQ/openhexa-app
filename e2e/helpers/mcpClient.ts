import {
  APIRequestContext,
  APIResponse,
  expect,
  request,
} from "@playwright/test";
import { createHash, randomBytes } from "node:crypto";

import { BASE_URL } from "../config/environment";

/** Where the authorization code is sent. Nothing serves it: the test answers the request itself. */
export const MCP_REDIRECT_URI = "http://127.0.0.1:8765/e2e-callback";

const base64url = (buffer: Buffer) => buffer.toString("base64url");

/**
 * An MCP client of the test's own: registered through dynamic client
 * registration, authorized by the user in the browser, then calling the MCP
 * endpoint with the token it is issued. Its requests carry no cookies, so the
 * token alone authenticates them, as for a real client: a request context
 * made inside a test otherwise inherits the project's signed-in storage state.
 */
export class McpClient {
  private readonly verifier = base64url(randomBytes(32));
  private readonly state = base64url(randomBytes(8));

  private constructor(
    private readonly api: APIRequestContext,
    readonly name: string,
    readonly clientId: string,
  ) {}

  static async register(name: string): Promise<McpClient> {
    const api = await request.newContext({
      baseURL: BASE_URL,
      storageState: { cookies: [], origins: [] },
    });
    const response = await api.post("/oauth/register/", {
      data: {
        client_name: name,
        redirect_uris: [MCP_REDIRECT_URI],
        token_endpoint_auth_method: "none",
      },
    });
    expect(response.status(), await response.text()).toBe(201);
    const { client_id } = await response.json();
    return new McpClient(api, name, client_id);
  }

  /** The authorization request a client opens in the user's browser. */
  get authorizeUrl(): string {
    const challenge = base64url(
      createHash("sha256").update(this.verifier).digest(),
    );
    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: MCP_REDIRECT_URI,
      response_type: "code",
      scope: "openhexa:mcp",
      state: this.state,
      code_challenge: challenge,
      code_challenge_method: "S256",
    });
    return `/oauth/authorize/?${params}`;
  }

  /** Trades the code the consent screen issued for an access token. */
  async exchangeCode(code: string): Promise<string> {
    const response = await this.api.post("/oauth/token/", {
      form: {
        grant_type: "authorization_code",
        code,
        redirect_uri: MCP_REDIRECT_URI,
        client_id: this.clientId,
        code_verifier: this.verifier,
      },
    });
    expect(response.ok(), await response.text()).toBe(true);
    return (await response.json()).access_token;
  }

  private rpc(
    token: string,
    method: string,
    params: Record<string, unknown> = {},
  ): Promise<APIResponse> {
    return this.api.post("/mcp/", {
      headers: { Authorization: `Bearer ${token}` },
      data: { jsonrpc: "2.0", id: 1, method, params },
    });
  }

  /** The tools the server advertises to this token, sorted by name. */
  async listTools(token: string): Promise<string[]> {
    const response = await this.rpc(token, "tools/list");
    expect(response.status(), await response.text()).toBe(200);
    const { result } = await response.json();
    return result.tools.map((tool: { name: string }) => tool.name).sort();
  }

  /** The text a tool call answers: its result, or the refusal. */
  async callTool(
    token: string,
    name: string,
    args: Record<string, unknown> = {},
  ): Promise<string> {
    const response = await this.rpc(token, "tools/call", {
      name,
      arguments: args,
    });
    expect(response.status(), await response.text()).toBe(200);
    const { result } = await response.json();
    return result.content[0].text;
  }

  /** The status the endpoint answers the token; 401 once revoked. */
  async statusOf(token: string): Promise<number> {
    return (await this.rpc(token, "tools/list")).status();
  }

  async dispose() {
    await this.api.dispose();
  }
}
