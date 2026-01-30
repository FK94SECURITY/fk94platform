"""
FK94 Security Platform - Wallet Deep Scan Service
Detects exchange interactions, mixer usage, OFAC sanctions, and calculates traceability score.
"""
import httpx
from datetime import datetime
from typing import Optional
from app.core.config import settings
from app.models.schemas import ExchangeInteraction, RiskLevel

# === Known Exchange Addresses (ETH) ===
# Sources: Etherscan labels, public documentation
KNOWN_EXCHANGE_ADDRESSES_ETH: dict[str, str] = {
    # Binance
    "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance",
    "0xd551234ae421e3bcba99a0da6d736074f22192ff": "Binance",
    "0x564286362092d8e7936f0549571a803b203aaced": "Binance",
    "0x0681d8db095565fe8a346fa0277bffde9c0edbbf": "Binance",
    "0xfe9e8709d3215310075d67e3ed32a380ccf451c8": "Binance",
    "0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67": "Binance",
    "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8": "Binance",
    "0xf977814e90da44bfa03b6295a0616a897441acec": "Binance",
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance",
    # Coinbase
    "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase",
    "0x503828976d22510aad0201ac7ec88293211571c7": "Coinbase",
    "0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740": "Coinbase",
    "0x3cd751e6b0078be393132286c442345e68ff0aaa": "Coinbase",
    "0xb5d85cbf7cb3ee0d56b3bb207d5fc4b82f43f511": "Coinbase",
    "0xeb2629a2734e272bcc07bda959863f316f4bd4cf": "Coinbase",
    "0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43": "Coinbase",
    # Kraken
    "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0": "Kraken",
    "0x53d284357ec70ce289d6d64134dfac8e511c8a3d": "Kraken",
    "0x2910543af39aba0cd09dbb2d50200b3e800a63d2": "Kraken",
    "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13": "Kraken",
    # OKX (formerly OKEx)
    "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b": "OKX",
    "0x236f9f97e0e62388479bf9e5ba4889e46b0273c3": "OKX",
    "0xa7efae728d2936e78bda97dc267687568dd593f3": "OKX",
    "0x5041ed759dd4afc3a72b8192c143f72f4724081a": "OKX",
    # Huobi (HTX)
    "0xab5c66752a9e8167967685f1450532fb96d5d24f": "Huobi",
    "0x6748f50f686bfbca6fe8ad62b22228b87f31ff2b": "Huobi",
    "0xfdb16996831753d5331ff813c29a93c76834a0ad": "Huobi",
    "0xeee28d484628d41a82d01a21dc91b1cdaf45c5b5": "Huobi",
    "0x5c985e89dde482efe97ea9f1950ad149eb73829b": "Huobi",
    # Bitfinex
    "0x876eabf441b2ee5b5b0554fd502a8e0600950cfa": "Bitfinex",
    "0xc6cde7c39eb2f0f0095f41570af89efc2c1ea828": "Bitfinex",
    "0x742d35cc6634c0532925a3b844bc9e7595f2bd33": "Bitfinex",
    # Gate.io
    "0x0d0707963952f2fba59dd06f2b425ace40b492fe": "Gate.io",
    "0x1c4b70a3968436b9a0a9cf5205c787eb81bb558c": "Gate.io",
    "0xd793281b45ce0ea2e5e5b0c72bed98cb8426cf8b": "Gate.io",
    # Crypto.com
    "0x6262998ced04146fa42253a5c0af90ca02dfd2a3": "Crypto.com",
    "0x46340b20830761efd32832a74d7169b29feb9758": "Crypto.com",
    # Bybit
    "0xf89d7b9c864f589bbf53a82105107622b35eaa40": "Bybit",
    "0xa7a93fd0a276fc1c0197a5b5623ed117786bac38": "Bybit",
    # KuCoin
    "0x2b5634c42055806a59e9107ed44d43c426e58258": "KuCoin",
    "0x689c56aef474df92d44a1b70850f808488f9769c": "KuCoin",
    "0xa1d8d972560c2f8144af871db508f0b0b10a3fbf": "KuCoin",
    # Gemini
    "0xd24400ae8bfebb18ca49be86258a3c749cf46853": "Gemini",
    "0x6fc82a5fe25a5cdb58bc74600a40a69c065263f8": "Gemini",
    # Bitstamp
    "0x00bdb5699745f5b860228c8f939abf1b9ae374ed": "Bitstamp",
    "0x1522900b6dafac587d499a862861c0869be6e428": "Bitstamp",
}

# === Known Exchange Addresses (BTC) ===
KNOWN_EXCHANGE_ADDRESSES_BTC: dict[str, str] = {
    # Binance
    "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo": "Binance",
    "3JZq4atUahhuA9rLhXLMhhTo133J9rF97j": "Binance",
    "bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3": "Binance",
    # Coinbase
    "3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS": "Coinbase",
    "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh": "Coinbase",
    "3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb": "Coinbase",
    # Kraken
    "3AfwAkvVDvbj5G3e2rCaDHgNLqf4q7hKqo": "Kraken",
    "bc1qr4dl5wa7kl8yu792dceg9z5knl2gkn220lk7a9": "Kraken",
    # Bitfinex
    "3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r": "Bitfinex",
    "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97": "Bitfinex",
    # Bitstamp
    "3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt": "Bitstamp",
    # OKX
    "bc1q2s3rjwvam9dt2ftt4sqxqjf3twav0gdx0k0q2etjz": "OKX",
}

# === Tornado Cash Addresses (ETH mixer) ===
TORNADO_CASH_ADDRESSES: dict[str, str] = {
    "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc": "Tornado Cash 0.1 ETH",
    "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936": "Tornado Cash 1 ETH",
    "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf": "Tornado Cash 10 ETH",
    "0xa160cdab225685da1d56aa342ad8841c3b53f291": "Tornado Cash 100 ETH",
    "0xd4b88df4d29f5cedd6857912842cff3b20c8cfa3": "Tornado Cash 100 ETH (old)",
    "0xfd8610d20aa15b7b2e3be39b396a1bc3516c7144": "Tornado Cash 100 ETH (old2)",
    "0x722122df12d4e14e13ac3b6895a86e84145b6967": "Tornado Cash Router",
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": "Tornado Cash Governance",
    "0x905b63fff465b9ffbf41dea908ceb12cd9f0d1ac": "Tornado Cash Mining",
    "0x178169b423a011fff22b9e3f3abea13414ddd0f1": "Tornado Cash Relayer",
    "0x610b717796ad172b316836ac95a2ffad065ceab4": "Tornado Cash Relayer 2",
    "0xbb93e510bbcd0b7beb5a853875f9ec60275cf498": "Tornado Cash Relayer 3",
}

# Chainalysis Sanctions Oracle contract on Ethereum mainnet
CHAINALYSIS_SANCTIONS_ORACLE = "0x40C57923924B5c5c5455c48D93317139ADDaC8fb"


async def deep_scan_eth(address: str) -> dict:
    """
    Deep scan an Ethereum address: fetch transactions and cross-reference
    with known exchange addresses and mixers.
    """
    address = address.lower()
    api_key = settings.ETHERSCAN_API_KEY
    params_base: dict = {"module": "account", "address": address}
    if api_key:
        params_base["apikey"] = api_key

    exchange_interactions: list[ExchangeInteraction] = []
    mixer_interactions: list[str] = []
    exchanges_detected: set[str] = set()
    counterparties: set[str] = set()
    first_tx_date: Optional[str] = None
    last_tx_date: Optional[str] = None
    warnings: list[str] = []
    balance: Optional[str] = None
    tx_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Get balance
        try:
            resp = await client.get("https://api.etherscan.io/api", params={
                **params_base, "action": "balance", "tag": "latest"
            })
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "1":
                    wei = int(data.get("result", 0))
                    balance = f"{wei / 1e18:.6f} ETH"
        except Exception:
            pass

        # 2. Fetch transaction list (up to 10000)
        try:
            resp = await client.get("https://api.etherscan.io/api", params={
                **params_base,
                "action": "txlist",
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": 10000,
                "sort": "asc",
            })
            if resp.status_code == 200:
                data = resp.json()
                txs = data.get("result", [])
                if isinstance(txs, list):
                    tx_count = len(txs)

                    for tx in txs:
                        from_addr = tx.get("from", "").lower()
                        to_addr = tx.get("to", "").lower()
                        tx_hash = tx.get("hash", "")
                        value_wei = int(tx.get("value", "0"))
                        value_eth = f"{value_wei / 1e18:.6f} ETH"
                        ts = tx.get("timeStamp", "")

                        # Track timestamps
                        if ts:
                            try:
                                dt = datetime.utcfromtimestamp(int(ts))
                                dt_str = dt.strftime("%Y-%m-%d %H:%M")
                                if first_tx_date is None:
                                    first_tx_date = dt_str
                                last_tx_date = dt_str
                            except (ValueError, OSError):
                                pass

                        # Determine counterparty
                        if from_addr == address:
                            counterparty = to_addr
                            direction = "sent"
                        else:
                            counterparty = from_addr
                            direction = "received"

                        if counterparty:
                            counterparties.add(counterparty)

                        # Check exchange match
                        exchange_name = KNOWN_EXCHANGE_ADDRESSES_ETH.get(counterparty)
                        if exchange_name:
                            exchanges_detected.add(exchange_name)
                            exchange_interactions.append(ExchangeInteraction(
                                exchange=exchange_name,
                                address=counterparty,
                                direction=direction,
                                tx_hash=tx_hash,
                                value=value_eth,
                                timestamp=dt_str if ts else None,
                            ))

                        # Check mixer match
                        mixer_name = TORNADO_CASH_ADDRESSES.get(counterparty)
                        if mixer_name:
                            mixer_interactions.append(
                                f"{direction} via {mixer_name} (tx: {tx_hash[:16]}...)"
                            )
        except Exception as e:
            warnings.append(f"Error fetching transactions: {str(e)[:80]}")

    return {
        "balance": balance,
        "tx_count": tx_count,
        "exchange_interactions": exchange_interactions,
        "exchanges_detected": sorted(exchanges_detected),
        "mixer_interactions": mixer_interactions,
        "used_mixer": len(mixer_interactions) > 0,
        "counterparties": len(counterparties),
        "first_tx_date": first_tx_date,
        "last_tx_date": last_tx_date,
        "warnings": warnings,
    }


async def deep_scan_btc(address: str) -> dict:
    """
    Deep scan a Bitcoin address: fetch transactions from blockchain.info
    and cross-reference with known exchange addresses.
    """
    exchange_interactions: list[ExchangeInteraction] = []
    exchanges_detected: set[str] = set()
    counterparties: set[str] = set()
    first_tx_date: Optional[str] = None
    last_tx_date: Optional[str] = None
    warnings: list[str] = []
    balance: Optional[str] = None
    tx_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                f"https://blockchain.info/rawaddr/{address}",
                params={"limit": 100},
            )
            if resp.status_code == 200:
                data = resp.json()
                sat_balance = data.get("final_balance", 0)
                balance = f"{sat_balance / 1e8:.8f} BTC"
                tx_count = data.get("n_tx", 0)

                for tx in data.get("txs", []):
                    tx_hash = tx.get("hash", "")
                    ts = tx.get("time", 0)
                    dt_str = None
                    if ts:
                        try:
                            dt = datetime.utcfromtimestamp(ts)
                            dt_str = dt.strftime("%Y-%m-%d %H:%M")
                            if first_tx_date is None:
                                first_tx_date = dt_str
                            last_tx_date = dt_str
                        except (ValueError, OSError):
                            pass

                    # Collect all output addresses
                    input_addrs = set()
                    for inp in tx.get("inputs", []):
                        prev = inp.get("prev_out", {})
                        addr = prev.get("addr", "")
                        if addr:
                            input_addrs.add(addr)

                    output_addrs = set()
                    for out in tx.get("out", []):
                        addr = out.get("addr", "")
                        if addr:
                            output_addrs.add(addr)

                    # Determine direction
                    if address in input_addrs:
                        direction = "sent"
                        related = output_addrs - {address}
                    else:
                        direction = "received"
                        related = input_addrs - {address}

                    for cp in related:
                        counterparties.add(cp)
                        exchange_name = KNOWN_EXCHANGE_ADDRESSES_BTC.get(cp)
                        if exchange_name:
                            exchanges_detected.add(exchange_name)
                            exchange_interactions.append(ExchangeInteraction(
                                exchange=exchange_name,
                                address=cp,
                                direction=direction,
                                tx_hash=tx_hash,
                                timestamp=dt_str,
                            ))
        except Exception as e:
            warnings.append(f"Error fetching BTC transactions: {str(e)[:80]}")

    # Sort timestamps for BTC (txs come newest first)
    if first_tx_date and last_tx_date and first_tx_date > last_tx_date:
        first_tx_date, last_tx_date = last_tx_date, first_tx_date

    return {
        "balance": balance,
        "tx_count": tx_count,
        "exchange_interactions": exchange_interactions,
        "exchanges_detected": sorted(exchanges_detected),
        "mixer_interactions": [],
        "used_mixer": False,
        "counterparties": len(counterparties),
        "first_tx_date": first_tx_date,
        "last_tx_date": last_tx_date,
        "warnings": warnings,
    }


async def check_ofac_eth(address: str) -> bool:
    """
    Query the Chainalysis Sanctions Oracle (on-chain, free) to check
    if an Ethereum address is sanctioned by OFAC.
    Uses eth_call to the oracle contract's isSanctioned(address) function.
    """
    address = address.lower()
    # isSanctioned(address) selector = 0xdfb80831
    # ABI-encode the address parameter (32 bytes, zero-padded)
    addr_padded = address.replace("0x", "").zfill(64)
    call_data = "0xdfb80831" + addr_padded

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            params: dict = {
                "module": "proxy",
                "action": "eth_call",
                "to": CHAINALYSIS_SANCTIONS_ORACLE,
                "data": call_data,
                "tag": "latest",
            }
            if settings.ETHERSCAN_API_KEY:
                params["apikey"] = settings.ETHERSCAN_API_KEY

            resp = await client.get("https://api.etherscan.io/api", params=params)
            if resp.status_code == 200:
                data = resp.json()
                result = data.get("result", "0x")
                # Result is a bool: 0x...01 = true (sanctioned), 0x...00 = false
                if result and len(result) >= 66:
                    return result[-1] == "1"
    except Exception:
        pass
    return False


def calculate_traceability_score(scan_result: dict, ofac_sanctioned: bool) -> tuple[int, list[str]]:
    """
    Calculate a traceability score from 0 (anonymous) to 100 (fully traceable).
    Returns (score, details_list).
    """
    score = 0
    details: list[str] = []

    # Exchange interactions are the biggest traceability signal
    exchanges = scan_result.get("exchanges_detected", [])
    interactions = scan_result.get("exchange_interactions", [])

    if len(exchanges) > 0:
        # Each unique exchange adds points
        exchange_points = min(len(exchanges) * 15, 45)
        score += exchange_points
        details.append(
            f"Interacted with {len(exchanges)} exchange(s): {', '.join(exchanges)} (+{exchange_points})"
        )

    # Number of exchange transactions
    if len(interactions) >= 10:
        score += 15
        details.append(f"{len(interactions)} exchange transactions detected (+15)")
    elif len(interactions) >= 3:
        score += 10
        details.append(f"{len(interactions)} exchange transactions detected (+10)")
    elif len(interactions) >= 1:
        score += 5
        details.append(f"{len(interactions)} exchange transaction(s) detected (+5)")

    # Sent to exchange = deposited = higher traceability (KYC link)
    sent_to_exchange = [i for i in interactions if i.direction == "sent"]
    if len(sent_to_exchange) > 0:
        score += 15
        details.append(f"Deposited to exchange {len(sent_to_exchange)} time(s) - KYC link likely (+15)")

    # Mixer usage reduces traceability slightly but flags suspicion
    if scan_result.get("used_mixer"):
        score -= 10
        details.append("Used mixer (Tornado Cash) - reduced traceability but flagged (-10)")

    # OFAC sanction
    if ofac_sanctioned:
        score += 20
        details.append("Address is OFAC sanctioned - fully identified (+20)")

    # High transaction count = more data points
    tx_count = scan_result.get("tx_count", 0)
    if tx_count >= 100:
        score += 5
        details.append(f"High activity ({tx_count} txs) - more data points (+5)")

    # Many unique counterparties
    counterparties = scan_result.get("counterparties", 0)
    if counterparties >= 50:
        score += 5
        details.append(f"{counterparties} unique counterparties - large footprint (+5)")

    # Clamp to 0-100
    score = max(0, min(100, score))

    if score == 0:
        details.append("No exchange interactions detected - wallet appears anonymous")

    return score, details


def calculate_wallet_risk(
    traceability_score: int,
    ofac_sanctioned: bool,
    used_mixer: bool,
    exchanges_detected: list[str],
) -> RiskLevel:
    """Calculate risk level based on traceability and flags."""
    if ofac_sanctioned:
        return RiskLevel.CRITICAL

    if used_mixer and traceability_score >= 50:
        return RiskLevel.HIGH

    if traceability_score >= 70:
        return RiskLevel.HIGH
    elif traceability_score >= 40:
        return RiskLevel.MEDIUM
    elif traceability_score >= 10:
        return RiskLevel.LOW
    else:
        return RiskLevel.SAFE
