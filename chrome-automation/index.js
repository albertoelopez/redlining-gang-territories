#!/usr/bin/env node

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require("@modelcontextprotocol/sdk/types.js");
const puppeteer = require("puppeteer-core");

let browser = null;
let page = null;

const server = new Server(
  {
    name: "chrome-automation-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "connect_to_chrome",
        description: "Connect to an existing Chrome browser with remote debugging enabled. Start Chrome with: chrome.exe --remote-debugging-port=9222",
        inputSchema: {
          type: "object",
          properties: {
            port: {
              type: "number",
              description: "The debugging port (default: 9222)",
              default: 9222,
            },
          },
        },
      },
      {
        name: "navigate",
        description: "Navigate to a URL",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "The URL to navigate to",
            },
          },
          required: ["url"],
        },
      },
      {
        name: "screenshot",
        description: "Take a screenshot of the current page",
        inputSchema: {
          type: "object",
          properties: {
            filename: {
              type: "string",
              description: "Filename to save (optional)",
            },
          },
        },
      },
      {
        name: "click",
        description: "Click on an element by selector or text",
        inputSchema: {
          type: "object",
          properties: {
            selector: {
              type: "string",
              description: "CSS selector or XPath",
            },
            text: {
              type: "string",
              description: "Text content to find and click",
            },
          },
        },
      },
      {
        name: "type_text",
        description: "Type text into an input field",
        inputSchema: {
          type: "object",
          properties: {
            selector: {
              type: "string",
              description: "CSS selector for the input",
            },
            text: {
              type: "string",
              description: "Text to type",
            },
          },
          required: ["selector", "text"],
        },
      },
      {
        name: "upload_file",
        description: "Upload a file using a file input",
        inputSchema: {
          type: "object",
          properties: {
            selector: {
              type: "string",
              description: "CSS selector for the file input",
            },
            filepath: {
              type: "string",
              description: "Path to the file to upload",
            },
          },
          required: ["filepath"],
        },
      },
      {
        name: "evaluate",
        description: "Execute JavaScript in the browser context",
        inputSchema: {
          type: "object",
          properties: {
            script: {
              type: "string",
              description: "JavaScript code to execute",
            },
          },
          required: ["script"],
        },
      },
      {
        name: "get_page_content",
        description: "Get the text content or HTML of the page",
        inputSchema: {
          type: "object",
          properties: {
            html: {
              type: "boolean",
              description: "Return HTML instead of text",
              default: false,
            },
          },
        },
      },
      {
        name: "wait_for_selector",
        description: "Wait for an element to appear",
        inputSchema: {
          type: "object",
          properties: {
            selector: {
              type: "string",
              description: "CSS selector to wait for",
            },
            timeout: {
              type: "number",
              description: "Timeout in milliseconds",
              default: 30000,
            },
          },
          required: ["selector"],
        },
      },
      {
        name: "list_tabs",
        description: "List all open browser tabs",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "switch_tab",
        description: "Switch to a different tab by index",
        inputSchema: {
          type: "object",
          properties: {
            index: {
              type: "number",
              description: "Tab index (0-based)",
            },
          },
          required: ["index"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "connect_to_chrome": {
        const port = args?.port || 9222;
        browser = await puppeteer.connect({
          browserURL: `http://127.0.0.1:${port}`,
          defaultViewport: null,
        });
        const pages = await browser.pages();
        page = pages[0] || await browser.newPage();
        return {
          content: [
            {
              type: "text",
              text: `Connected to Chrome on port ${port}. Found ${pages.length} tabs. Current page: ${page.url()}`,
            },
          ],
        };
      }

      case "navigate": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");
        await page.goto(args.url, { waitUntil: "networkidle2", timeout: 60000 });
        return {
          content: [
            {
              type: "text",
              text: `Navigated to: ${args.url}\nPage title: ${await page.title()}`,
            },
          ],
        };
      }

      case "screenshot": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");
        const filename = args?.filename || `screenshot_${Date.now()}.png`;
        const filepath = `/mnt/d/AI_Projects/chrome-automation-mcp/${filename}`;
        await page.screenshot({ path: filepath, fullPage: false });
        return {
          content: [
            {
              type: "text",
              text: `Screenshot saved to: ${filepath}`,
            },
          ],
        };
      }

      case "click": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");
        if (args.text) {
          await page.evaluate((text) => {
            const elements = [...document.querySelectorAll("*")];
            const el = elements.find((e) => e.textContent.includes(text) && e.children.length === 0);
            if (el) el.click();
            else throw new Error(`Element with text "${text}" not found`);
          }, args.text);
        } else if (args.selector) {
          await page.click(args.selector);
        }
        return {
          content: [{ type: "text", text: `Clicked: ${args.selector || args.text}` }],
        };
      }

      case "type_text": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");
        await page.type(args.selector, args.text);
        return {
          content: [{ type: "text", text: `Typed text into: ${args.selector}` }],
        };
      }

      case "upload_file": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");

        // Find file input or wait for file chooser
        if (args.selector) {
          const input = await page.$(args.selector);
          await input.uploadFile(args.filepath);
        } else {
          // Handle file chooser dialog
          const [fileChooser] = await Promise.all([
            page.waitForFileChooser(),
            page.click('input[type="file"]'),
          ]);
          await fileChooser.accept([args.filepath]);
        }
        return {
          content: [{ type: "text", text: `Uploaded file: ${args.filepath}` }],
        };
      }

      case "evaluate": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");
        const result = await page.evaluate(args.script);
        return {
          content: [
            {
              type: "text",
              text: `Result: ${JSON.stringify(result, null, 2)}`,
            },
          ],
        };
      }

      case "get_page_content": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");
        const content = args?.html
          ? await page.content()
          : await page.evaluate(() => document.body.innerText);
        return {
          content: [{ type: "text", text: content.substring(0, 50000) }],
        };
      }

      case "wait_for_selector": {
        if (!page) throw new Error("Not connected. Call connect_to_chrome first.");
        await page.waitForSelector(args.selector, { timeout: args.timeout || 30000 });
        return {
          content: [{ type: "text", text: `Found element: ${args.selector}` }],
        };
      }

      case "list_tabs": {
        if (!browser) throw new Error("Not connected. Call connect_to_chrome first.");
        const pages = await browser.pages();
        const tabs = await Promise.all(
          pages.map(async (p, i) => `${i}: ${await p.title()} - ${p.url()}`)
        );
        return {
          content: [{ type: "text", text: tabs.join("\n") }],
        };
      }

      case "switch_tab": {
        if (!browser) throw new Error("Not connected. Call connect_to_chrome first.");
        const pages = await browser.pages();
        if (args.index >= pages.length) throw new Error(`Tab ${args.index} not found`);
        page = pages[args.index];
        await page.bringToFront();
        return {
          content: [
            {
              type: "text",
              text: `Switched to tab ${args.index}: ${await page.title()}`,
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Chrome Automation MCP server running");
}

main().catch(console.error);
