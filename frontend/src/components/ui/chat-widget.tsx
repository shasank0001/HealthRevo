import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Lightbulb, User, Send } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatWidgetProps {
  patientId: string;
  className?: string;
}

export function ChatWidget({ patientId, className }: ChatWidgetProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm your AI health assistant. I can help explain your health data, answer medication questions, and provide guidance. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const res = await api.sendChatMessage(patientId, message);
      return { response: res.content, timestamp: res.timestamp.toISOString() };
    },
  onSuccess: (data) => {
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          timestamp: new Date(),
        },
      ]);
    },
    onError: (error) => {
      console.error("Chat error:", error);
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later or contact your healthcare provider for urgent concerns.",
          timestamp: new Date(),
        },
      ]);
    },
  });

  const handleSendMessage = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    chatMutation.mutate(input.trim());
    setInput("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`bg-card rounded-lg border border-border shadow-sm h-[600px] flex flex-col ${className}`} data-testid="chat-widget">
      <div className="p-6 border-b border-border">
        <h2 className="text-xl font-semibold text-foreground">AI Health Assistant</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Ask questions about your health, medications, or risk scores
        </p>
      </div>

      <ScrollArea className="flex-1 p-6">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start space-x-3 ${
                message.role === "user" ? "justify-end" : ""
              }`}
              data-testid={`message-${message.role}-${index}`}
            >
              {message.role === "assistant" && (
                <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                  <Lightbulb className="w-4 h-4 text-primary-foreground" />
                </div>
              )}
              
              <div
                className={`p-3 rounded-lg max-w-md ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>

              {message.role === "user" && (
                <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-secondary-foreground" />
                </div>
              )}
            </div>
          ))}
          
          {chatMutation.isPending && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <Lightbulb className="w-4 h-4 text-primary-foreground" />
              </div>
              <div className="bg-muted p-3 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="p-6 border-t border-border">
        <div className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your health..."
            disabled={chatMutation.isPending}
            data-testid="input-chat-message"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!input.trim() || chatMutation.isPending}
            data-testid="button-send-message"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          ⚠️ This AI assistant provides general information only and should not replace professional medical advice.
        </p>
      </div>
    </div>
  );
}
