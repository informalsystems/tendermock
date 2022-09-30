# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: cosmos/vesting/v1beta1/tx.proto, cosmos/vesting/v1beta1/vesting.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import Dict, List, Optional

import betterproto
from betterproto.grpc.grpclib_server import ServiceBase
import grpclib


@dataclass(eq=False, repr=False)
class BaseVestingAccount(betterproto.Message):
    """
    BaseVestingAccount implements the VestingAccount interface. It contains all
    the necessary fields needed for any vesting account implementation.
    """

    base_account: "__auth_v1_beta1__.BaseAccount" = betterproto.message_field(1)
    original_vesting: List["__base_v1_beta1__.Coin"] = betterproto.message_field(2)
    delegated_free: List["__base_v1_beta1__.Coin"] = betterproto.message_field(3)
    delegated_vesting: List["__base_v1_beta1__.Coin"] = betterproto.message_field(4)
    end_time: int = betterproto.int64_field(5)


@dataclass(eq=False, repr=False)
class ContinuousVestingAccount(betterproto.Message):
    """
    ContinuousVestingAccount implements the VestingAccount interface. It
    continuously vests by unlocking coins linearly with respect to time.
    """

    base_vesting_account: "BaseVestingAccount" = betterproto.message_field(1)
    start_time: int = betterproto.int64_field(2)


@dataclass(eq=False, repr=False)
class DelayedVestingAccount(betterproto.Message):
    """
    DelayedVestingAccount implements the VestingAccount interface. It vests all
    coins after a specific time, but non prior. In other words, it keeps them
    locked until a specified time.
    """

    base_vesting_account: "BaseVestingAccount" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class Period(betterproto.Message):
    """Period defines a length of time and amount of coins that will vest."""

    length: int = betterproto.int64_field(1)
    amount: List["__base_v1_beta1__.Coin"] = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class PeriodicVestingAccount(betterproto.Message):
    """
    PeriodicVestingAccount implements the VestingAccount interface. It
    periodically vests by unlocking coins during each specified period.
    """

    base_vesting_account: "BaseVestingAccount" = betterproto.message_field(1)
    start_time: int = betterproto.int64_field(2)
    vesting_periods: List["Period"] = betterproto.message_field(3)


@dataclass(eq=False, repr=False)
class PermanentLockedAccount(betterproto.Message):
    """
    PermanentLockedAccount implements the VestingAccount interface. It does not
    ever release coins, locking them indefinitely. Coins in this account can
    still be used for delegating and for governance votes even while locked.
    Since: cosmos-sdk 0.43
    """

    base_vesting_account: "BaseVestingAccount" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class MsgCreateVestingAccount(betterproto.Message):
    """
    MsgCreateVestingAccount defines a message that enables creating a vesting
    account.
    """

    from_address: str = betterproto.string_field(1)
    to_address: str = betterproto.string_field(2)
    amount: List["__base_v1_beta1__.Coin"] = betterproto.message_field(3)
    end_time: int = betterproto.int64_field(4)
    delayed: bool = betterproto.bool_field(5)


@dataclass(eq=False, repr=False)
class MsgCreateVestingAccountResponse(betterproto.Message):
    """
    MsgCreateVestingAccountResponse defines the Msg/CreateVestingAccount
    response type.
    """

    pass


class MsgStub(betterproto.ServiceStub):
    async def create_vesting_account(
        self,
        *,
        from_address: str = "",
        to_address: str = "",
        amount: Optional[List["__base_v1_beta1__.Coin"]] = None,
        end_time: int = 0,
        delayed: bool = False
    ) -> "MsgCreateVestingAccountResponse":
        amount = amount or []

        request = MsgCreateVestingAccount()
        request.from_address = from_address
        request.to_address = to_address
        if amount is not None:
            request.amount = amount
        request.end_time = end_time
        request.delayed = delayed

        return await self._unary_unary(
            "/cosmos.vesting.v1beta1.Msg/CreateVestingAccount",
            request,
            MsgCreateVestingAccountResponse,
        )


class MsgBase(ServiceBase):
    async def create_vesting_account(
        self,
        from_address: str,
        to_address: str,
        amount: Optional[List["__base_v1_beta1__.Coin"]],
        end_time: int,
        delayed: bool,
    ) -> "MsgCreateVestingAccountResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_create_vesting_account(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "from_address": request.from_address,
            "to_address": request.to_address,
            "amount": request.amount,
            "end_time": request.end_time,
            "delayed": request.delayed,
        }

        response = await self.create_vesting_account(**request_kwargs)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/cosmos.vesting.v1beta1.Msg/CreateVestingAccount": grpclib.const.Handler(
                self.__rpc_create_vesting_account,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgCreateVestingAccount,
                MsgCreateVestingAccountResponse,
            ),
        }


from ...auth import v1beta1 as __auth_v1_beta1__
from ...base import v1beta1 as __base_v1_beta1__
