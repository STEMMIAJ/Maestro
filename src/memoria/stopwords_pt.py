"""Stop words PT-BR + EN para extração de tópicos."""

STOPWORDS = {
    # Português
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo",
    "as", "ate", "com", "como", "da", "das", "de", "dela", "delas", "dele",
    "deles", "depois", "do", "dos", "e", "ela", "elas", "ele", "eles", "em",
    "entre", "era", "essa", "essas", "esse", "esses", "esta", "estas", "este",
    "estes", "eu", "foi", "foram", "ha", "isso", "isto", "ja", "la", "lhe",
    "lhes", "lo", "mais", "mas", "me", "mesmo", "meu", "minha", "muito",
    "na", "nao", "nas", "nem", "no", "nos", "nossa", "nossas", "nosso",
    "nossos", "num", "numa", "nuns", "nus", "os", "ou", "para", "pela",
    "pelas", "pelo", "pelos", "por", "qual", "quando", "que", "quem", "sao",
    "se", "sem", "ser", "sera", "seu", "seus", "sua", "suas", "tambem",
    "te", "tem", "tinha", "toda", "todas", "todo", "todos", "tu", "tua",
    "tudo", "um", "uma", "umas", "uns", "voce", "voces", "vos",
    # Português acentuado (para match direto)
    "até", "não", "já", "há", "é", "está", "são", "será", "também",
    "então", "você", "vocês", "através", "após", "além", "só", "porém",
    "próprio", "própria", "seria", "porque", "ainda", "onde", "pode",
    "podem", "cada", "sobre", "deve", "assim", "outro", "outra", "outros",
    "outras", "fazer", "feito", "sendo", "sido", "ter", "tendo",
    # Inglês (comum no código)
    "the", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "shall", "can", "need", "must", "it", "its", "this", "that",
    "these", "those", "and", "but", "or", "not", "no", "so", "if", "then",
    "than", "too", "very", "just", "about", "above", "after", "again",
    "all", "also", "an", "any", "at", "because", "before", "between",
    "both", "by", "from", "for", "get", "got", "here", "how", "in",
    "into", "my", "of", "on", "only", "other", "our", "out", "over",
    "own", "same", "she", "he", "some", "such", "them", "there", "they",
    "to", "up", "us", "we", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "you", "your",
    # Termos Claude Code (ruído)
    "tool", "use", "result", "content", "type", "text", "input", "output",
    "file", "path", "name", "value", "true", "false", "null", "none",
    "function", "return", "import", "class", "def", "self", "args",
    "error", "data", "json", "string", "list", "dict", "int", "str",
}
