Web search
==========

Allow models to search the web for the latest information before generating a response.

Web search allows models to access up-to-date information from the internet and provide answers with sourced citations. To enable this, use the web search tool in the Responses API or, in some cases, Chat Completions.

There are three main types of web search available with OpenAI models:

1.  Non‑reasoning web search: The non-reasoning model sends the user’s query to the web search tool, which returns the response based on top results. There’s no internal planning and the model simply passes along the search tool’s responses. This method is fast and ideal for quick lookups.
2.  Agentic search with reasoning models is an approach where the model actively manages the search process. It can perform web searches as part of its chain of thought, analyze results, and decide whether to keep searching. This flexibility makes agentic search well suited to complex workflows, but it also means searches take longer than quick lookups. For example, you can adjust GPT-5’s reasoning level to change both the depth and latency of the search.
3.  Deep research is a specialized, agent-driven method for in-depth, extended investigations by reasoning models. The model conducts web searches as part of its chain of thought, often tapping into hundreds of sources. Deep research can run for several minutes and is best used with background mode. These tasks typically use models like `o3-deep-research`, `o4-mini-deep-research`, or `gpt-5` with reasoning level set to `high`.

Using the [Responses API](/docs/api-reference/responses), you can enable web search by configuring it in the `tools` array in an API request to generate content. Like any other tool, the model can choose to search the web or not based on the content of the input prompt.

Web search tool example

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.create({
    model: "gpt-5",
    tools: [
        { type: "web_search" },
    ],
    input: "What was a positive news story from today?",
});

console.log(response.output_text);
```

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    tools=[{"type": "web_search"}],
    input="What was a positive news story from today?"
)

print(response.output_text)
```

```bash
curl "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-5",
        "tools": [{"type": "web_search"}],
        "input": "what was a positive news story from today?"
    }'
```

Web search tool versions
------------------------

The `web_search` tool is generally available with the Responses API, and is compatible with the models:

*   gpt-4o-mini
*   gpt-4o
*   gpt-4.1-mini
*   gpt-4.1
*   o4-mini
*   o3
*   gpt-5 with reasoning levels `low`, `medium` and `high`

The previous version the web search tool, `web_search_preview` , is still available with both the Chat Completions API and the Responses API; it points to a dated version`web_search_preview_2025_03_11`. As the tool evolves, future dated snapshot versions will be documented in the [API reference](/docs/api-reference/responses/create).

Output and citations
--------------------

Model responses that use the web search tool will include two parts:

*   A `web_search_call` output item with the ID of the search call, along with the action taken in `web_search_call.action`. The action is one of:
    *   `search`, which represents a web search. It will usually (but not always) includes the search `query` and `domains` which were searched. Search actions incur a tool call cost (see [pricing](/docs/pricing#built-in-tools)).
    *   `open_page`, which represents a page being opened. Only emitted by Deep Research models.
    *   `find_in_page`, which represents searching within a page. Only emitted by Deep Research models.
*   A `message` output item containing:
    *   The text result in `message.content[0].text`
    *   Annotations `message.content[0].annotations` for the cited URLs

By default, the model's response will include inline citations for URLs found in the web search results. In addition to this, the `url_citation` annotation object will contain the URL, title and location of the cited source.

When displaying web results or information contained in web results to end users, inline citations must be made clearly visible and clickable in your user interface.

```json
[
    {
        "type": "web_search_call",
        "id": "ws_67c9fa0502748190b7dd390736892e100be649c1a5ff9609",
        "status": "completed"
    },
    {
        "id": "msg_67c9fa077e288190af08fdffda2e34f20be649c1a5ff9609",
        "type": "message",
        "status": "completed",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": "On March 6, 2025, several news...",
                "annotations": [
                    {
                        "type": "url_citation",
                        "start_index": 2606,
                        "end_index": 2758,
                        "url": "https://...",
                        "title": "Title..."
                    }
                ]
            }
        ]
    }
]
```

Domain filtering
----------------

Domain filtering in web search lets you limit results to a specific set of domains. With the `filters` parameter you can set an allow-list of up to 20 domains. When formatting domain URLs, omit the HTTP or HTTPS prefix. For example, use [`openai.com`](http://openai.com) instead of [`https://openai.com/`](https://openai.com/). This approach also includes subdomains in the search. Note that domain filtering is only available in the Responses API with the `web_search` tool.

Sources
-------

To get greater visibility into the actual domains used by the web search tool, use `sources`. This returns all the sources the model referenced when forming its response. The difference between citations and sources is that citations are optional, and there are often fewer citations than the total number of source URLs searched. Citations appear inline with the response, while sources provide developers with the full list of domains. Third-party specialized domains used during search are labeled as `oai-sports`, `oai-weather`, or `oai-finance`. Sources are available with both the `web_search` and `web_search_preview` tools.

List sources

```bash
curl "https://api.openai.com/v1/responses" -H "Content-Type: application/json" -H "Authorization: Bearer $OPENAI_API_KEY" -d '{
  "model": "gpt-5",
  "reasoning": { "effort": "low" },
  "tools": [
    {
      "type": "web_search",
      "filters": {
        "allowed_domains": [
          "pubmed.ncbi.nlm.nih.gov",
          "clinicaltrials.gov",
          "www.who.int",
          "www.cdc.gov",
          "www.fda.gov"
        ]
      }
    }
  ],
  "tool_choice": "auto",
  "include": ["web_search_call.action.sources"],
  "input": "Please perform a web search on how semaglutide is used in the treatment of diabetes."
}'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.create({
model: "gpt-5",
reasoning: { effort: "low" },
tools: [
{
type: "web_search",
filters: {
allowed_domains: [
"pubmed.ncbi.nlm.nih.gov",
"clinicaltrials.gov",
"www.who.int",
"www.cdc.gov",
"www.fda.gov"
]
}
}
],
tool_choice: "auto",
include: ["web_search_call.action.sources"],
input: "Please perform a web search on how semaglutide is used in the treatment of diabetes."
});

console.log(response.output_text);
```

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
model="gpt-5",
reasoning={"effort": "low"},
tools=[
{
"type": "web_search",
"filters": {
"allowed_domains": [
"pubmed.ncbi.nlm.nih.gov",
"clinicaltrials.gov",
"www.who.int",
"www.cdc.gov",
"www.fda.gov"
]
}
}
],
tool_choice="auto",
include=["web_search_call.action.sources"],
input="Please perform a web search on how semaglutide is used in the treatment of diabetes."
)

print(response.output_text)
```

User location
-------------

To refine search results based on geography, you can specify an approximate user location using country, city, region, and/or timezone.

*   The `city` and `region` fields are free text strings, like `Minneapolis` and `Minnesota` respectively.
*   The `country` field is a two-letter [ISO country code](https://en.wikipedia.org/wiki/ISO_3166-1), like `US`.
*   The `timezone` field is an [IANA timezone](https://timeapi.io/documentation/iana-timezones) like `America/Chicago`.

Note that user location is not supported for deep research models using web search.

Customizing user location

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="o4-mini",
    tools=[{
        "type": "web_search",
        "user_location": {
            "type": "approximate",
            "country": "GB",
            "city": "London",
            "region": "London",
        }
    }],
    input="What are the best restaurants around Granary Square?",
)

print(response.output_text)
```

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
    model: "o4-mini",
    tools: [{
        type: "web_search",
        user_location: {
            type: "approximate",
            country: "GB",
            city: "London",
            region: "London"
        }
    }],
    input: "What are the best restaurants around Granary Square?",
});
console.log(response.output_text);
```

```bash
curl "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "o4-mini",
        "tools": [{
            "type": "web_search",
            "user_location": {
                "type": "approximate",
                "country": "GB",
                "city": "London",
                "region": "London"
            }
        }],
        "input": "What are the best restaurants around Granary Square?"
    }'
```

Search context size
-------------------

When using this tool, the `search_context_size` parameter controls how much context is retrieved from the web to help the tool formulate a response. The tokens used by the search tool do **not** affect the context window of the main model specified in the `model` parameter in your response creation request. These tokens are also **not** carried over from one turn to another — they're simply used to formulate the tool response and then discarded.

Choosing a context size impacts:

*   **Cost**: Search content tokens are free for some models, but may be billed at a model's text token rates for others. Refer to [pricing](/docs/pricing#built-in-tools) for details.
*   **Quality**: Higher search context sizes generally provide richer context, resulting in more accurate, comprehensive answers.
*   **Latency**: Higher context sizes require processing more tokens, which can slow down the tool's response time.

Available values:

*   **`high`**: Most comprehensive context, slower response.
*   **`medium`** (default): Balanced context and latency.
*   **`low`**: Least context, fastest response, but potentially lower answer quality.

Context size configuration is not supported for o3, o3-pro, o4-mini, and deep research models.

Customizing search context size

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "web_search_preview",
        "search_context_size": "low",
    }],
    input="What movie won best picture in 2025?",
)

print(response.output_text)
```

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
    model: "gpt-4.1",
    tools: [{
        type: "web_search_preview",
        search_context_size: "low",
    }],
    input: "What movie won best picture in 2025?",
});
console.log(response.output_text);
```

```bash
curl "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-4.1",
        "tools": [{
            "type": "web_search_preview",
            "search_context_size": "low"
        }],
        "input": "What movie won best picture in 2025?"
    }'
```

Usage notes
-----------

||
|ResponsesChat CompletionsAssistants|Same as tiered rate limits for underlying model used with the tool.|PricingZDR and data residency|

#### Limitations

*   Web search is currently not supported in [`gpt-5`](/docs/models/gpt-5) with `minimal` [`gpt-4.1-nano`](/docs/models/gpt-4.1-nano) model.
*   When used as a tool in the [Responses API](/docs/api-reference/responses), web search has the same tiered rate limits as the models above.
*   Web search is limited to a context window size of 128000 (even with [`gpt-4.1`](/docs/models/gpt-4.1) and [`gpt-4.1-mini`](/docs/models/gpt-4.1-mini) models).
*   [Refer to this guide](/docs/guides/your-data) for data handling, residency, and retention information.



Libraries
=========

Set up your development environment to use the OpenAI API with an SDK in your preferred language.

This page covers setting up your local development environment to use the [OpenAI API](/docs/api-reference). You can use one of our officially supported SDKs, a community library, or your own preferred HTTP client.

Create and export an API key
----------------------------

Before you begin, [create an API key in the dashboard](/api-keys), which you'll use to securely [access the API](/docs/api-reference/authentication). Store the key in a safe location, like a [`.zshrc` file](https://www.freecodecamp.org/news/how-do-zsh-configuration-files-work/) or another text file on your computer. Once you've generated an API key, export it as an [environment variable](https://en.wikipedia.org/wiki/Environment_variable) in your terminal.

macOS / Linux

Export an environment variable on macOS or Linux systems

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Windows

Export an environment variable in PowerShell

```bash
setx OPENAI_API_KEY "your_api_key_here"
```

OpenAI SDKs are configured to automatically read your API key from the system environment.

Install an official SDK
-----------------------

JavaScript

To use the OpenAI API in server-side JavaScript environments like Node.js, Deno, or Bun, you can use the official [OpenAI SDK for TypeScript and JavaScript](https://github.com/openai/openai-node). Get started by installing the SDK using [npm](https://www.npmjs.com/) or your preferred package manager:

Install the OpenAI SDK with npm

```bash
npm install openai
```

With the OpenAI SDK installed, create a file called `example.mjs` and copy the example code into it:

Test a basic API request

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.create({
    model: "gpt-5",
    input: "Write a one-sentence bedtime story about a unicorn."
});

console.log(response.output_text);
```

Execute the code with `node example.mjs` (or the equivalent command for Deno or Bun). In a few moments, you should see the output of your API request.

[

Learn more on GitHub

Discover more SDK capabilities and options on the library's GitHub README.

](https://github.com/openai/openai-node)

Python

To use the OpenAI API in Python, you can use the official [OpenAI SDK for Python](https://github.com/openai/openai-python). Get started by installing the SDK using [pip](https://pypi.org/project/pip/):

Install the OpenAI SDK with pip

```bash
pip install openai
```

With the OpenAI SDK installed, create a file called `example.py` and copy the example code into it:

Test a basic API request

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
```

Execute the code with `python example.py`. In a few moments, you should see the output of your API request.

[

Learn more on GitHub

Discover more SDK capabilities and options on the library's GitHub README.

](https://github.com/openai/openai-python)

.NET

In collaboration with Microsoft, OpenAI provides an officially supported API client for C#. You can install it with the .NET CLI from [NuGet](https://www.nuget.org/).

```text
dotnet add package OpenAI
```

A simple API request to [Chat Completions](/docs/api-reference/chat) would look like this:

```csharp
using OpenAI.Chat;

ChatClient client = new(
  model: "gpt-4.1", 
  apiKey: Environment.GetEnvironmentVariable("OPENAI_API_KEY")
);

ChatCompletion completion = client.CompleteChat("Say 'this is a test.'");

Console.WriteLine($"[ASSISTANT]: {completion.Content[0].Text}");
```

To learn more about using the OpenAI API in .NET, check out the GitHub repo linked below!

[

Learn more on GitHub

Discover more SDK capabilities and options on the library's GitHub README.

](https://github.com/openai/openai-dotnet)

Java

OpenAI provides an API helper for the Java programming language, currently in beta. You can include the Maven dependency using the following configuration:

```xml
<dependency>
    <groupId>com.openai</groupId>
    <artifactId>openai-java</artifactId>
    <version>0.31.0</version>
</dependency>
```

A simple API request to [Chat Completions](/docs/api-reference/chat) would look like this:

```java
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.ChatCompletion;
import com.openai.models.ChatCompletionCreateParams;
import com.openai.models.ChatModel;

// Configures using the `OPENAI_API_KEY`, `OPENAI_ORG_ID` and `OPENAI_PROJECT_ID`
// environment variables
OpenAIClient client = OpenAIOkHttpClient.fromEnv();

ChatCompletionCreateParams params = ChatCompletionCreateParams.builder()
    .addUserMessage("Say this is a test")
    .model(ChatModel.O3_MINI)
    .build();
ChatCompletion chatCompletion = client.chat().completions().create(params);
```

To learn more about using the OpenAI API in Java, check out the GitHub repo linked below!

[

Learn more on GitHub

Discover more SDK capabilities and options on the library's GitHub README.

](https://github.com/openai/openai-java)

Go

OpenAI provides an API helper for the Go programming language, currently in beta. You can import the library using the code below:

```golang
import (
  "github.com/openai/openai-go" // imported as openai
)
```

A simple API request to [Chat Completions](/docs/api-reference/chat) would look like this:

```golang
package main

import (
  "context"
  "fmt"

  "github.com/openai/openai-go"
  "github.com/openai/openai-go/option"
)

func main() {
  client := openai.NewClient(
    option.WithAPIKey("My API Key"), // defaults to os.LookupEnv("OPENAI_API_KEY")
  )
  chatCompletion, err := client.Chat.Completions.New(
    context.TODO(), openai.ChatCompletionNewParams{
      Messages: openai.F(
        []openai.ChatCompletionMessageParamUnion{
          openai.UserMessage("Say this is a test"),
        }
      ),
      Model: openai.F(openai.ChatModelGPT4o),
    }
  )

  if err != nil {
    panic(err.Error())
  }

  println(chatCompletion.Choices[0].Message.Content)
}
```

To learn more about using the OpenAI API in Go, check out the GitHub repo linked below!

[

Learn more on GitHub

Discover more SDK capabilities and options on the library's GitHub README.

](https://github.com/openai/openai-go)

Azure OpenAI libraries
----------------------

Microsoft's Azure team maintains libraries that are compatible with both the OpenAI API and Azure OpenAI services. Read the library documentation below to learn how you can use them with the OpenAI API.

*   [Azure OpenAI client library for .NET](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/openai/Azure.AI.OpenAI)
*   [Azure OpenAI client library for JavaScript](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/openai/openai)
*   [Azure OpenAI client library for Java](https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/openai/azure-ai-openai)
*   [Azure OpenAI client library for Go](https://github.com/Azure/azure-sdk-for-go/tree/main/sdk/ai/azopenai)

* * *

Community libraries
-------------------

The libraries below are built and maintained by the broader developer community. You can also [watch our OpenAPI specification](https://github.com/openai/openai-openapi) repository on GitHub to get timely updates on when we make changes to our API.

Please note that OpenAI does not verify the correctness or security of these projects. **Use them at your own risk!**

### C# / .NET

*   [Betalgo.OpenAI](https://github.com/betalgo/openai) by [Betalgo](https://github.com/betalgo)
*   [OpenAI-API-dotnet](https://github.com/OkGoDoIt/OpenAI-API-dotnet) by [OkGoDoIt](https://github.com/OkGoDoIt)
*   [OpenAI-DotNet](https://github.com/RageAgainstThePixel/OpenAI-DotNet) by [RageAgainstThePixel](https://github.com/RageAgainstThePixel)

### C++

*   [liboai](https://github.com/D7EAD/liboai) by [D7EAD](https://github.com/D7EAD)

### Clojure

*   [openai-clojure](https://github.com/wkok/openai-clojure) by [wkok](https://github.com/wkok)

### Crystal

*   [openai-crystal](https://github.com/sferik/openai-crystal) by [sferik](https://github.com/sferik)

### Dart/Flutter

*   [openai](https://github.com/anasfik/openai) by [anasfik](https://github.com/anasfik)

### Delphi

*   [DelphiOpenAI](https://github.com/HemulGM/DelphiOpenAI) by [HemulGM](https://github.com/HemulGM)

### Elixir

*   [openai.ex](https://github.com/mgallo/openai.ex) by [mgallo](https://github.com/mgallo)

### Go

*   [go-gpt3](https://github.com/sashabaranov/go-gpt3) by [sashabaranov](https://github.com/sashabaranov)

### Java

*   [simple-openai](https://github.com/sashirestela/simple-openai) by [Sashir Estela](https://github.com/sashirestela)
*   [Spring AI](https://spring.io/projects/spring-ai)

### Julia

*   [OpenAI.jl](https://github.com/rory-linehan/OpenAI.jl) by [rory-linehan](https://github.com/rory-linehan)

### Kotlin

*   [openai-kotlin](https://github.com/Aallam/openai-kotlin) by [Mouaad Aallam](https://github.com/Aallam)

### Node.js

*   [openai-api](https://www.npmjs.com/package/openai-api) by [Njerschow](https://github.com/Njerschow)
*   [openai-api-node](https://www.npmjs.com/package/openai-api-node) by [erlapso](https://github.com/erlapso)
*   [gpt-x](https://www.npmjs.com/package/gpt-x) by [ceifa](https://github.com/ceifa)
*   [gpt3](https://www.npmjs.com/package/gpt3) by [poteat](https://github.com/poteat)
*   [gpts](https://www.npmjs.com/package/gpts) by [thencc](https://github.com/thencc)
*   [@dalenguyen/openai](https://www.npmjs.com/package/@dalenguyen/openai) by [dalenguyen](https://github.com/dalenguyen)
*   [tectalic/openai](https://github.com/tectalichq/public-openai-client-js) by [tectalic](https://tectalic.com/)

### PHP

*   [orhanerday/open-ai](https://packagist.org/packages/orhanerday/open-ai) by [orhanerday](https://github.com/orhanerday)
*   [tectalic/openai](https://github.com/tectalichq/public-openai-client-php) by [tectalic](https://tectalic.com/)
*   [openai-php client](https://github.com/openai-php/client) by [openai-php](https://github.com/openai-php)

### Python

*   [chronology](https://github.com/OthersideAI/chronology) by [OthersideAI](https://www.othersideai.com/)

### R

*   [rgpt3](https://github.com/ben-aaron188/rgpt3) by [ben-aaron188](https://github.com/ben-aaron188)

### Ruby

*   [openai](https://github.com/nileshtrivedi/openai/) by [nileshtrivedi](https://github.com/nileshtrivedi)
*   [ruby-openai](https://github.com/alexrudall/ruby-openai) by [alexrudall](https://github.com/alexrudall)

### Rust

*   [async-openai](https://github.com/64bit/async-openai) by [64bit](https://github.com/64bit)
*   [fieri](https://github.com/lbkolev/fieri) by [lbkolev](https://github.com/lbkolev)

### Scala

*   [openai-scala-client](https://github.com/cequence-io/openai-scala-client) by [cequence-io](https://github.com/cequence-io)

### Swift

*   [AIProxySwift](https://github.com/lzell/AIProxySwift) by [Lou Zell](https://github.com/lzell)
*   [OpenAIKit](https://github.com/dylanshine/openai-kit) by [dylanshine](https://github.com/dylanshine)
*   [OpenAI](https://github.com/MacPaw/OpenAI/) by [MacPaw](https://github.com/MacPaw)

### Unity

*   [OpenAi-Api-Unity](https://github.com/hexthedev/OpenAi-Api-Unity) by [hexthedev](https://github.com/hexthedev)
*   [com.openai.unity](https://github.com/RageAgainstThePixel/com.openai.unity) by [RageAgainstThePixel](https://github.com/RageAgainstThePixel)

### Unreal Engine

*   [OpenAI-Api-Unreal](https://github.com/KellanM/OpenAI-Api-Unreal) by [KellanM](https://github.com/KellanM)

Other OpenAI repositories
-------------------------

*   [tiktoken](https://github.com/openai/tiktoken) - counting tokens
*   [simple-evals](https://github.com/openai/simple-evals) - simple evaluation library
*   [mle-bench](https://github.com/openai/mle-bench) - library to evaluate machine learning engineer agents
*   [gym](https://github.com/openai/gym) - reinforcement learning library
*   [swarm](https://github.com/openai/swarm) - educational orchestration repository
