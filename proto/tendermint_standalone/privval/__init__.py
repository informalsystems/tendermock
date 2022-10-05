# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: tendermint/privval/service.proto, tendermint/privval/types.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import Dict

import betterproto
from betterproto.grpc.grpclib_server import ServiceBase
import grpclib


class Errors(betterproto.Enum):
    ERRORS_UNKNOWN = 0
    ERRORS_UNEXPECTED_RESPONSE = 1
    ERRORS_NO_CONNECTION = 2
    ERRORS_CONNECTION_TIMEOUT = 3
    ERRORS_READ_TIMEOUT = 4
    ERRORS_WRITE_TIMEOUT = 5


@dataclass(eq=False, repr=False)
class RemoteSignerError(betterproto.Message):
    code: int = betterproto.int32_field(1)
    description: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class PubKeyRequest(betterproto.Message):
    """
    PubKeyRequest requests the consensus public key from the remote signer.
    """

    chain_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class PubKeyResponse(betterproto.Message):
    """PubKeyResponse is a response message containing the public key."""

    pub_key: "_crypto__.PublicKey" = betterproto.message_field(1)
    error: "RemoteSignerError" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class SignVoteRequest(betterproto.Message):
    """SignVoteRequest is a request to sign a vote"""

    vote: "_types__.Vote" = betterproto.message_field(1)
    chain_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class SignedVoteResponse(betterproto.Message):
    """
    SignedVoteResponse is a response containing a signed vote or an error
    """

    vote: "_types__.Vote" = betterproto.message_field(1)
    error: "RemoteSignerError" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class SignProposalRequest(betterproto.Message):
    """SignProposalRequest is a request to sign a proposal"""

    proposal: "_types__.Proposal" = betterproto.message_field(1)
    chain_id: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class SignedProposalResponse(betterproto.Message):
    """
    SignedProposalResponse is response containing a signed proposal or an error
    """

    proposal: "_types__.Proposal" = betterproto.message_field(1)
    error: "RemoteSignerError" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class PingRequest(betterproto.Message):
    """PingRequest is a request to confirm that the connection is alive."""

    pass


@dataclass(eq=False, repr=False)
class PingResponse(betterproto.Message):
    """PingResponse is a response to confirm that the connection is alive."""

    pass


@dataclass(eq=False, repr=False)
class Message(betterproto.Message):
    pub_key_request: "PubKeyRequest" = betterproto.message_field(1, group="sum")
    pub_key_response: "PubKeyResponse" = betterproto.message_field(2, group="sum")
    sign_vote_request: "SignVoteRequest" = betterproto.message_field(3, group="sum")
    signed_vote_response: "SignedVoteResponse" = betterproto.message_field(
        4, group="sum"
    )
    sign_proposal_request: "SignProposalRequest" = betterproto.message_field(
        5, group="sum"
    )
    signed_proposal_response: "SignedProposalResponse" = betterproto.message_field(
        6, group="sum"
    )
    ping_request: "PingRequest" = betterproto.message_field(7, group="sum")
    ping_response: "PingResponse" = betterproto.message_field(8, group="sum")


@dataclass(eq=False, repr=False)
class AuthSigMessage(betterproto.Message):
    """
    AuthSigMessage is duplicated from p2p prior to the P2P refactor. It is used
    for the SecretConnection until we migrate privval to gRPC.
    https://github.com/tendermint/tendermint/issues/4698
    """

    pub_key: "_crypto__.PublicKey" = betterproto.message_field(1)
    sig: bytes = betterproto.bytes_field(2)


class PrivValidatorApiStub(betterproto.ServiceStub):
    async def get_pub_key(self, *, chain_id: str = "") -> "PubKeyResponse":

        request = PubKeyRequest()
        request.chain_id = chain_id

        return await self._unary_unary(
            "/tendermint.privval.PrivValidatorAPI/GetPubKey", request, PubKeyResponse
        )

    async def sign_vote(
        self, *, vote: "_types__.Vote" = None, chain_id: str = ""
    ) -> "SignedVoteResponse":

        request = SignVoteRequest()
        if vote is not None:
            request.vote = vote
        request.chain_id = chain_id

        return await self._unary_unary(
            "/tendermint.privval.PrivValidatorAPI/SignVote", request, SignedVoteResponse
        )

    async def sign_proposal(
        self, *, proposal: "_types__.Proposal" = None, chain_id: str = ""
    ) -> "SignedProposalResponse":

        request = SignProposalRequest()
        if proposal is not None:
            request.proposal = proposal
        request.chain_id = chain_id

        return await self._unary_unary(
            "/tendermint.privval.PrivValidatorAPI/SignProposal",
            request,
            SignedProposalResponse,
        )


class PrivValidatorApiBase(ServiceBase):
    async def get_pub_key(self, chain_id: str) -> "PubKeyResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def sign_vote(
        self, vote: "_types__.Vote", chain_id: str
    ) -> "SignedVoteResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def sign_proposal(
        self, proposal: "_types__.Proposal", chain_id: str
    ) -> "SignedProposalResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_get_pub_key(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "chain_id": request.chain_id,
        }

        response = await self.get_pub_key(**request_kwargs)
        await stream.send_message(response)

    async def __rpc_sign_vote(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "vote": request.vote,
            "chain_id": request.chain_id,
        }

        response = await self.sign_vote(**request_kwargs)
        await stream.send_message(response)

    async def __rpc_sign_proposal(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "proposal": request.proposal,
            "chain_id": request.chain_id,
        }

        response = await self.sign_proposal(**request_kwargs)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/tendermint.privval.PrivValidatorAPI/GetPubKey": grpclib.const.Handler(
                self.__rpc_get_pub_key,
                grpclib.const.Cardinality.UNARY_UNARY,
                PubKeyRequest,
                PubKeyResponse,
            ),
            "/tendermint.privval.PrivValidatorAPI/SignVote": grpclib.const.Handler(
                self.__rpc_sign_vote,
                grpclib.const.Cardinality.UNARY_UNARY,
                SignVoteRequest,
                SignedVoteResponse,
            ),
            "/tendermint.privval.PrivValidatorAPI/SignProposal": grpclib.const.Handler(
                self.__rpc_sign_proposal,
                grpclib.const.Cardinality.UNARY_UNARY,
                SignProposalRequest,
                SignedProposalResponse,
            ),
        }


from .. import crypto as _crypto__
from .. import types as _types__
