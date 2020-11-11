

    #Abstract

    #Introdução

    #Resultados esperados

    #Cronograma e planejamento


    O modelo de Information Centric Network (ICN) é uma alternativa ao paradigma centrado em hosts, usado em larga escala em toda a infraestrutura da rede global de internet. Neste, um canal de comunicação entre dois clientes é determinado por um par de endereços IP origem e destino, de forma que mensagens são trocadas enviando dados com endereço de destino conhecido e explícito. Uma alternativa a este cenário é uma abordagem orientada à distribuição de conteúdo, em que mensagens de interesse são enviadas por clientes e propagadas pela rede. Cada nodo, ao receber a mensagem, pode determinar se possui o dado, e portanto responde à mensagem, ou se não o possui e deve enviar o pedido a diante.

    O uso de tal abordagem depende da implementação de um protocolo único entre todos os usuários da rede e portanto só é possível em casos restritos onde todos os dispositivos estão executando uma aplicação compatível. O contexto de redes ad-hoc é ideal para a adoção deste mecanismo devido ao número de clientes relativamente baixo e por ser uma rede independente e separada das demais. Inclusive sendo possível o uso de um mecanismo de conversão para que a comunicação com redes externas ainda seja possível.

    Portanto o cenário de redes de aplicações de Comando e Controle (C2) é um candidato perfeito à adoção, já que tipicamente consiste em um número limitado de dispositivos homogênios com conectividade entre si e baixa demanda de comunicação com redes externas.

    Neste caso de uso, são necessários baixa latência e alta disponibilidade. Ao passo em que a infraestrutura é limitada e conta uma topologia dinâmica de conexões intermitentes e sem fio composta por dispositivos que, em sua maioria, são móveis e tem capacidades de processamento e armazenamento reduzidas. Aplicando a abordagem ICN, os dados podem ser dissemidados pela rede e armazenados em cache, fazendo com que eventuais perdas de conexão tenham suas consequências amenizadas, o uso da já limitada banda seja reduzido e os tempos de resposta entre solicitação e recebimento de dados sejam diminuídos.






    O modelo de aplicação de Comando e Controle (C2) usado se beneficia muito da topologia ad-hoc com um número limitado de usuários e tem foco na otimimização do tempo de entrega dos pacotes. Usando o paradigma ICN (Information Centric Network) ao invés do HCN (Host Centric Network), elimimanos a necessidade de os usuários explicitamente destinarem seus pacotes de dados a hosts especificos. O que, por sua vez, diminui a complexidade e o overhead de processamento da aplicação C2 nos clientes, já que os os mecanismos de distribuição de dados com base em mensagens de interesse são de responsabilidade da interface de rede dos dispositivos compatíveis.