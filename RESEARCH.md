# Research — 21 October 2026

Demand is **inferred**, not a verified request for this tool. A compatible-looking record change can fail on a missing reader default or one writer union branch.

[Exact Most-stars search](https://github.com/search?q=avro+schema&type=repositories&s=stars&o=desc), observed 2026-10-21T06:19:15.182Z. Highest-star relevant comparable found in the inspected pool: `apache/avro`. This is not an exhaustive global ranking.

| Comparable | Stars | Last push | License metadata | Observed workflow |
| --- | ---: | --- | --- | --- |
| [apache/avro](https://github.com/apache/avro) | 3305 | 2026-10-18T17:39:33Z | Apache-2.0 | Multilanguage Avro schemas, serialization and compatibility machinery. |
| [confluentinc/schema-registry](https://github.com/confluentinc/schema-registry) | 2470 | 2026-10-21T05:27:11Z | NOASSERTION | Versioned registry and compatibility service; Kafka ecosystem integration. |
| [fastavro/fastavro](https://github.com/fastavro/fastavro) | 714 | 2026-10-15T13:13:40Z | MIT | Python serialization library; README explicitly says maintenance mode. |

## Choice and tradeoffs

Explain bounded Avro writer-to-reader resolution with field paths, promotions, defaults and union branch evidence. schema-gen generates JSON models and npm/export tools inspect packages. This traces actual Avro reader/writer evolution rules; it is separate from spreadsheet, streaming, stock and text-merge contracts.

The established alternatives are broader and often the better choice for their supported ecosystems. This tool provides one bounded inspectable report with an invented example and no runtime dependencies. READMEs/docs were read for install and example workflow; competitor clean install, time to first useful result, reliability, support response and performance were not measured. Own tests prove only the documented subset. Stars are research context, not performance or adoption evidence.

Keyword search coverage is narrow: Avro results include generators/profilers, event-time results include general streaming platforms, inventory-expiry results include unrelated homelab/certificate inventory, and three-way results include plugins and unrelated scraped text. Known relevant established tools were added directly. Spreadsheet comparison uses Excelize rather than an obsolete GitHub openpyxl mirror.

[Exact metadata and sampled current issues/PRs](RESEARCH_PROVENANCE.json). The samples are context, not verified competitor defects or requests for our new tool. Relevant Avro compatibility, POI SharedFormula and Git merge-file source was inspected; standard algorithms are original reimplementations. Microsoft CellFormula and Beam semantics informed the bounded contracts. No third-party code, branding or prose is copied.

Primary references:
- https://avro.apache.org/docs/1.12.0/specification/
