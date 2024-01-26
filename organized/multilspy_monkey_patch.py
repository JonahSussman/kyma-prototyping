import asyncio
import logging
import pathlib
import os
import threading
import json
from pathlib import PurePath

from typing import AsyncIterator, Any, Iterator, List, Dict, Union, Tuple
from typing_extensions import NotRequired, TypedDict
from contextlib import asynccontextmanager

from monitors4codegen.multilspy import multilspy_types
from monitors4codegen.multilspy import LanguageServer, SyncLanguageServer
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger
from monitors4codegen.multilspy.multilspy_exceptions import MultilspyException
from monitors4codegen.multilspy.lsp_protocol_handler import lsp_types
from monitors4codegen.multilspy.lsp_protocol_handler.lsp_requests import LspRequest
from monitors4codegen.multilspy.lsp_protocol_handler.lsp_constants import LSPConstants
from monitors4codegen.multilspy.language_servers.eclipse_jdtls.eclipse_jdtls import EclipseJDTLS

# Monkey patch some requests
# 
# Technically, there should be equivalent SyncLanguageServer implementations for
# each one of the LanguageServer methods, but that was a lot of extra code, and
# I'm not using SyncLanguageServer anyway. Additionally, there should be a
# corresponding method defined on LspRequest, but again... too lazy. It should
# look like this if I were doing it properly:

"""
def SyncLanguageServer_request_workspace_symbol(self, query: str) -> List[multilspy_types.UnifiedSymbolInformation]:
  result = asyncio.run_coroutine_threadsafe(
    self.language_server.request_workspace_symbol(query), self.loop
  ).result()
  return result

async def LspRequest_workspace_symbol(
  self, params: lsp_types.WorkspaceSymbolParams
) -> Union[List["lsp_types.SymbolInformation"], List["lsp_types.WorkspaceSymbol"], None]:
  return await self.send_request("workspace/symbol", params)

SyncLanguageServer.request_workspace_symbol = SyncLanguageServer_request_workspace_symbol
LspRequest.workspace_symbol = LspRequest_workspace_symbol
"""

# SyncLanguageServer wraps a LanguageServer. EclipseJDTLS is a LanguageServer.
# LanguageServer has a LanguageServerHandler attribute called 'server'.
# Confusing, I know.


async def LanguageServer_request_workspace_symbol(self: LanguageServer, query: str)  -> List[multilspy_types.UnifiedSymbolInformation]:
  if not self.server_started:
    self.logger.log(
      "request_workspace_symbols called before Language Server started",
      logging.ERROR,
    )
    raise MultilspyException("Language Server not started")
  
  response: Union[List["lsp_types.SymbolInformation"], List["lsp_types.WorkspaceSymbol"], None] = await self.server.send.send_request(
    "workspace/symbol",
    {
      "query": query,
    }
  )

  ret: List[multilspy_types.UnifiedSymbolInformation] = []

  assert isinstance(response, list)
  for item in response:
    assert isinstance(item, dict)
    assert LSPConstants.NAME in item
    assert LSPConstants.KIND in item

    ret.append(multilspy_types.UnifiedSymbolInformation(**item))

  return ret

LanguageServer.request_workspace_symbol = LanguageServer_request_workspace_symbol


async def LanguageServer_request_document_diagnostic(self: LanguageServer, relative_file_path: str) -> List[multilspy_types.UnifiedSymbolInformation]:
  if not self.server_started:
    self.logger.log(
      "request_document_diagnostic called before Language Server started",
      logging.ERROR,
    )
    raise MultilspyException("Language Server not started")
  
  with self.open_file(relative_file_path):
    response: lsp_types.DocumentDiagnosticReport = await self.server.send.send_request(
    "textDocument/diagnostic",
    {
      LSPConstants.TEXT_DOCUMENT: {
        LSPConstants.URI: pathlib.Path(
          str(PurePath(self.repository_root_path, relative_file_path))
        ).as_uri()
      }
    })

  return response

LanguageServer.request_document_diagnostic = LanguageServer_request_document_diagnostic


async def LanguageServer_execute_command(self: LanguageServer, command: str, arguments: List["Any"]):
  if not self.server_started:
    self.logger.log(
      "execute_command called before Language Server started",
      logging.ERROR,
    )
    raise MultilspyException("Language Server not started")

  return await self.server.send.send_request(
    "workspace/executeCommand",
    {
      "command": command,
      "arguments": arguments,
    }
  )

LanguageServer.execute_command = LanguageServer_execute_command

async def EclipseJDTLS_execute_command(self: EclipseJDTLS, command: str, arguments: List["Any"]):
  return await super(EclipseJDTLS, self).execute_command(command, [json.dumps(x) for x in arguments])

EclipseJDTLS.execute_command = EclipseJDTLS_execute_command


async def LanguageServer_request_workspace_references(self: LanguageServer, command: str, arguments: List["Any"]):
  if not self.server_started:
    self.logger.log(
      "request_workspace_references called before Language Server started",
      logging.ERROR,
    )
    raise MultilspyException("Language Server not started")

  return await self.server.send.send_request(
    "workspace/executeCommand",
    {
      "command": command,
      "arguments": arguments,
    }
  )

LanguageServer.request_workspace_references = LanguageServer_request_workspace_references


LanguageServer.diagnostics = {}
LanguageServer.diagnostics_conditions = {}
LanguageServer.diagnostics_conditions_lock = threading.Lock()

def LanguageServer_get_diagnostic(self: LanguageServer, uri: str, timeout: float = 30.0):
  # with self.diagnostics_conditions_lock:
  #   if uri not in self.diagnostics_conditions:
  #     self.diagnostics_conditions[uri] = threading.Condition()

  # cond: threading.Condition = self.diagnostics_conditions[uri]
  # with cond:
  #   did_timeout = False

  #   while not did_timeout and uri not in self.diagnostics:
  #     did_timeout = cond.wait(timeout)

  if uri in self.diagnostics:
    return (True, self.diagnostics[uri])
  else:
    return (False, None)

LanguageServer.get_diagnostic = LanguageServer_get_diagnostic


def start_server_decorator(start_server_method):
  @asynccontextmanager
  async def decorate_start_server(self: EclipseJDTLS):
    async with start_server_method(self):
      async def print_it(params):
        print(params)
        return
      
      async def handle_publish_diagnostic(params):
        # TODO: Support that whole "wait till the build is done" thing so we can
        # do incremental builds. Ask Jonah about what this means.

        # print('handle_publish_diagnostic')
        uri = params['uri']
        diagnostics = params['diagnostics']
        # print(f"uri: {uri}\ndiagnostics: {diagnostics}")

        # with self.diagnostics_conditions_lock:
        #   if uri not in self.diagnostics_conditions:
        #     self.diagnostics_conditions[uri] = threading.Condition()

        # cond: threading.Condition = self.diagnostics_conditions[uri]
        # with cond:
        self.diagnostics[uri] = diagnostics
          # cond.notify_all()

      self.server.on_notification("textDocument/publishDiagnostics", handle_publish_diagnostic)
      self.server.on_notification("language/actionableNotification", print_it)
      self.server.on_notification("language/status", print_it)

      yield self

  return decorate_start_server

EclipseJDTLS.start_server = start_server_decorator(EclipseJDTLS.start_server)