#!/usr/bin/env python3
"""
Birlikteyiz - Trade Panel with E-commerce Integration
Gamified ERP System with Real Marketplace Connectivity
"""

import pygame
import requests
import json
import asyncio
import websocket
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import threading
import time

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class NotificationType(Enum):
    NEW_ORDER = "new_order"
    PAYMENT_RECEIVED = "payment_received"
    STOCK_LOW = "stock_low"
    INVOICE_CREATED = "invoice_created"
    SHIPMENT_READY = "shipment_ready"
    CUSTOMER_MESSAGE = "customer_message"

@dataclass
class Product:
    id: str
    name: str
    sku: str
    price: float
    stock: int
    category: str
    marketplace: str
    image_url: str = ""
    description: str = ""

@dataclass
class Order:
    id: str
    customer_name: str
    customer_email: str
    products: List[Dict[str, Any]]
    total_amount: float
    status: OrderStatus
    marketplace: str
    order_date: datetime
    shipping_address: str
    notes: str = ""

@dataclass
class Notification:
    id: str
    type: NotificationType
    title: str
    message: str
    timestamp: datetime
    read: bool = False
    data: Dict[str, Any] = None

class SentosAPI:
    """Sentos E-commerce Integrator API Client"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.sentos.com.tr"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    async def get_orders(self, status: str = None, limit: int = 50) -> List[Order]:
        """Fetch orders from all connected marketplaces"""
        try:
            params = {'limit': limit}
            if status:
                params['status'] = status
            
            response = self.session.get(f"{self.base_url}/orders", params=params)
            response.raise_for_status()
            
            orders_data = response.json()
            orders = []
            
            for order_data in orders_data.get('orders', []):
                order = Order(
                    id=order_data['id'],
                    customer_name=order_data['customer']['name'],
                    customer_email=order_data['customer']['email'],
                    products=order_data['items'],
                    total_amount=float(order_data['total']),
                    status=OrderStatus(order_data['status']),
                    marketplace=order_data['marketplace'],
                    order_date=datetime.fromisoformat(order_data['created_at']),
                    shipping_address=order_data['shipping_address'],
                    notes=order_data.get('notes', '')
                )
                orders.append(order)
            
            return orders
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []
    
    async def get_products(self) -> List[Product]:
        """Fetch products from all connected marketplaces"""
        try:
            response = self.session.get(f"{self.base_url}/products")
            response.raise_for_status()
            
            products_data = response.json()
            products = []
            
            for product_data in products_data.get('products', []):
                product = Product(
                    id=product_data['id'],
                    name=product_data['name'],
                    sku=product_data['sku'],
                    price=float(product_data['price']),
                    stock=int(product_data['stock']),
                    category=product_data['category'],
                    marketplace=product_data['marketplace'],
                    image_url=product_data.get('image_url', ''),
                    description=product_data.get('description', '')
                )
                products.append(product)
            
            return products
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> bool:
        """Update order status"""
        try:
            data = {'status': status.value}
            response = self.session.put(f"{self.base_url}/orders/{order_id}", json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    async def create_invoice(self, order_id: str) -> Dict[str, Any]:
        """Create invoice for order"""
        try:
            response = self.session.post(f"{self.base_url}/orders/{order_id}/invoice")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating invoice: {e}")
            return {}

class TradePanel:
    """Modern Trade Panel with E-commerce Integration"""
    
    def __init__(self, screen, fonts, colors):
        self.screen = screen
        self.fonts = fonts
        self.colors = colors
        
        # API Integration
        self.sentos_api = SentosAPI("your_api_key_here")
        
        # Data
        self.orders = []
        self.products = []
        self.notifications = []
        
        # UI State
        self.current_tab = "orders"
        self.selected_order = None
        self.notification_count = 0
        
        # Panel dimensions
        self.panel_rect = pygame.Rect(300, 50, 700, 600)
        self.tab_height = 40
        
        # Real-time updates
        self.last_update = datetime.now()
        self.update_interval = 30  # seconds
        
        # Start background tasks
        self.start_background_tasks()
    
    def start_background_tasks(self):
        """Start background tasks for real-time updates"""
        def update_loop():
            while True:
                try:
                    # Update orders and products
                    asyncio.run(self.refresh_data())
                    time.sleep(self.update_interval)
                except Exception as e:
                    print(f"Background update error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    async def refresh_data(self):
        """Refresh orders and products from API"""
        try:
            # Fetch new orders
            new_orders = await self.sentos_api.get_orders()
            
            # Check for new orders and create notifications
            for order in new_orders:
                if order.id not in [o.id for o in self.orders]:
                    self.add_notification(
                        NotificationType.NEW_ORDER,
                        "Yeni Sipariş!",
                        f"{order.marketplace} - {order.customer_name} - {order.total_amount:.2f}₺",
                        {'order_id': order.id}
                    )
            
            self.orders = new_orders
            
            # Fetch products
            self.products = await self.sentos_api.get_products()
            
            # Check for low stock
            for product in self.products:
                if product.stock < 5:  # Low stock threshold
                    self.add_notification(
                        NotificationType.STOCK_LOW,
                        "Stok Azalıyor!",
                        f"{product.name} - Kalan: {product.stock}",
                        {'product_id': product.id}
                    )
            
        except Exception as e:
            print(f"Error refreshing data: {e}")
    
    def add_notification(self, type: NotificationType, title: str, message: str, data: Dict = None):
        """Add new notification"""
        notification = Notification(
            id=f"notif_{len(self.notifications)}_{int(time.time())}",
            type=type,
            title=title,
            message=message,
            timestamp=datetime.now(),
            data=data or {}
        )
        self.notifications.insert(0, notification)  # Add to beginning
        self.notification_count += 1
        
        # Keep only last 50 notifications
        if len(self.notifications) > 50:
            self.notifications = self.notifications[:50]
    
    def draw_panel_background(self, rect, panel_type="default"):
        """Draw modern panel background"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        if panel_type == "primary":
            bg_color = (*self.colors['primary_blue'], 220)
        elif panel_type == "dark":
            bg_color = (*self.colors['dark_gray'], 220)
        else:
            bg_color = (*self.colors['transparent_dark'], 220)
        
        pygame.draw.rect(panel_surface, bg_color, (0, 0, rect.width, rect.height))
        pygame.draw.rect(panel_surface, self.colors['border_light'], (0, 0, rect.width, rect.height), 2)
        
        self.screen.blit(panel_surface, rect.topleft)
    
    def draw_tabs(self):
        """Draw tab navigation"""
        tabs = [
            ("orders", "Siparişler"),
            ("products", "Ürünler"),
            ("analytics", "Analitik"),
            ("accounting", "Muhasebe"),
            ("notifications", f"Bildirimler ({self.notification_count})")
        ]
        
        tab_width = self.panel_rect.width // len(tabs)
        
        for i, (tab_id, tab_name) in enumerate(tabs):
            tab_rect = pygame.Rect(
                self.panel_rect.x + i * tab_width,
                self.panel_rect.y,
                tab_width,
                self.tab_height
            )
            
            # Tab background
            if tab_id == self.current_tab:
                tab_color = self.colors['accent_blue']
                text_color = self.colors['white']
            else:
                tab_color = self.colors['medium_gray']
                text_color = self.colors['text_secondary']
            
            pygame.draw.rect(self.screen, tab_color, tab_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], tab_rect, 1)
            
            # Tab text
            text_surface = self.fonts['medium'].render(tab_name, True, text_color)
            text_rect = text_surface.get_rect(center=tab_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_orders_tab(self):
        """Draw orders management tab"""
        content_rect = pygame.Rect(
            self.panel_rect.x,
            self.panel_rect.y + self.tab_height,
            self.panel_rect.width,
            self.panel_rect.height - self.tab_height
        )
        
        # Orders list
        order_list_rect = pygame.Rect(content_rect.x + 10, content_rect.y + 10, 400, content_rect.height - 20)
        self.draw_panel_background(order_list_rect, "dark")
        
        # Orders header
        header_text = self.fonts['large'].render("Siparişler", True, self.colors['text_primary'])
        self.screen.blit(header_text, (order_list_rect.x + 10, order_list_rect.y + 10))
        
        # Order items
        y_offset = 50
        for i, order in enumerate(self.orders[:10]):  # Show first 10 orders
            order_rect = pygame.Rect(
                order_list_rect.x + 5,
                order_list_rect.y + y_offset + i * 50,
                order_list_rect.width - 10,
                45
            )
            
            # Order background
            if self.selected_order and self.selected_order.id == order.id:
                order_bg_color = self.colors['accent_blue']
            else:
                order_bg_color = self.colors['light_gray']
            
            pygame.draw.rect(self.screen, order_bg_color, order_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], order_rect, 1)
            
            # Order info
            order_text = f"#{order.id[:8]} - {order.customer_name}"
            order_surface = self.fonts['medium'].render(order_text, True, self.colors['text_primary'])
            self.screen.blit(order_surface, (order_rect.x + 10, order_rect.y + 5))
            
            amount_text = f"{order.total_amount:.2f}₺ - {order.marketplace}"
            amount_surface = self.fonts['small'].render(amount_text, True, self.colors['text_secondary'])
            self.screen.blit(amount_surface, (order_rect.x + 10, order_rect.y + 25))
            
            # Status indicator
            status_color = self.get_status_color(order.status)
            status_rect = pygame.Rect(order_rect.right - 80, order_rect.y + 10, 70, 25)
            pygame.draw.rect(self.screen, status_color, status_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], status_rect, 1)
            
            status_text = self.fonts['small'].render(order.status.value.upper(), True, self.colors['white'])
            status_text_rect = status_text.get_rect(center=status_rect.center)
            self.screen.blit(status_text, status_text_rect)
        
        # Order details panel
        if self.selected_order:
            self.draw_order_details(content_rect.x + 420, content_rect.y + 10, 270, content_rect.height - 20)
    
    def draw_order_details(self, x, y, width, height):
        """Draw selected order details"""
        details_rect = pygame.Rect(x, y, width, height)
        self.draw_panel_background(details_rect, "primary")
        
        order = self.selected_order
        
        # Header
        header_text = self.fonts['large'].render("Sipariş Detayı", True, self.colors['text_primary'])
        self.screen.blit(header_text, (x + 10, y + 10))
        
        # Order info
        info_y = y + 50
        info_items = [
            f"Sipariş No: #{order.id[:12]}",
            f"Müşteri: {order.customer_name}",
            f"E-posta: {order.customer_email}",
            f"Pazaryeri: {order.marketplace}",
            f"Tutar: {order.total_amount:.2f}₺",
            f"Tarih: {order.order_date.strftime('%d.%m.%Y %H:%M')}",
            f"Durum: {order.status.value.upper()}"
        ]
        
        for i, info in enumerate(info_items):
            info_surface = self.fonts['small'].render(info, True, self.colors['text_primary'])
            self.screen.blit(info_surface, (x + 10, info_y + i * 20))
        
        # Products
        products_y = info_y + len(info_items) * 20 + 20
        products_header = self.fonts['medium'].render("Ürünler:", True, self.colors['text_primary'])
        self.screen.blit(products_header, (x + 10, products_y))
        
        for i, product in enumerate(order.products[:5]):  # Show first 5 products
            product_text = f"• {product['name']} x{product['quantity']}"
            product_surface = self.fonts['small'].render(product_text, True, self.colors['text_secondary'])
            self.screen.blit(product_surface, (x + 20, products_y + 25 + i * 18))
        
        # Action buttons
        buttons_y = y + height - 100
        self.draw_action_buttons(x + 10, buttons_y, width - 20)
    
    def draw_action_buttons(self, x, y, width):
        """Draw action buttons for order management"""
        button_height = 30
        button_spacing = 5
        
        buttons = [
            ("Hazırla", self.colors['green']),
            ("Fatura Kes", self.colors['orange']),
            ("Kargo Ver", self.colors['blue']),
            ("İptal Et", self.colors['red'])
        ]
        
        button_width = (width - (len(buttons) - 1) * button_spacing) // len(buttons)
        
        for i, (button_text, button_color) in enumerate(buttons):
            button_rect = pygame.Rect(
                x + i * (button_width + button_spacing),
                y + i * (button_height + button_spacing),
                button_width,
                button_height
            )
            
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], button_rect, 1)
            
            text_surface = self.fonts['small'].render(button_text, True, self.colors['white'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_products_tab(self):
        """Draw products management tab"""
        content_rect = pygame.Rect(
            self.panel_rect.x,
            self.panel_rect.y + self.tab_height,
            self.panel_rect.width,
            self.panel_rect.height - self.tab_height
        )
        
        self.draw_panel_background(content_rect, "dark")
        
        # Products grid
        header_text = self.fonts['large'].render("Ürün Yönetimi", True, self.colors['text_primary'])
        self.screen.blit(header_text, (content_rect.x + 10, content_rect.y + 10))
        
        # Product cards
        card_width = 200
        card_height = 120
        cards_per_row = 3
        
        for i, product in enumerate(self.products[:9]):  # Show first 9 products
            row = i // cards_per_row
            col = i % cards_per_row
            
            card_x = content_rect.x + 20 + col * (card_width + 10)
            card_y = content_rect.y + 50 + row * (card_height + 10)
            
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            # Card background
            pygame.draw.rect(self.screen, self.colors['medium_gray'], card_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], card_rect, 1)
            
            # Product info
            name_text = self.fonts['medium'].render(product.name[:20], True, self.colors['text_primary'])
            self.screen.blit(name_text, (card_x + 10, card_y + 10))
            
            price_text = self.fonts['small'].render(f"{product.price:.2f}₺", True, self.colors['text_accent'])
            self.screen.blit(price_text, (card_x + 10, card_y + 35))
            
            stock_color = self.colors['red'] if product.stock < 5 else self.colors['green']
            stock_text = self.fonts['small'].render(f"Stok: {product.stock}", True, stock_color)
            self.screen.blit(stock_text, (card_x + 10, card_y + 55))
            
            marketplace_text = self.fonts['small'].render(product.marketplace, True, self.colors['text_secondary'])
            self.screen.blit(marketplace_text, (card_x + 10, card_y + 75))
    
    def draw_analytics_tab(self):
        """Draw analytics and reports tab"""
        content_rect = pygame.Rect(
            self.panel_rect.x,
            self.panel_rect.y + self.tab_height,
            self.panel_rect.width,
            self.panel_rect.height - self.tab_height
        )
        
        self.draw_panel_background(content_rect, "dark")
        
        # Analytics header
        header_text = self.fonts['large'].render("Satış Analitikleri", True, self.colors['text_primary'])
        self.screen.blit(header_text, (content_rect.x + 10, content_rect.y + 10))
        
        # KPI Cards
        kpi_y = content_rect.y + 50
        kpis = [
            ("Günlük Satış", f"{sum(o.total_amount for o in self.orders if o.order_date.date() == datetime.now().date()):.2f}₺"),
            ("Toplam Sipariş", str(len(self.orders))),
            ("Ortalama Sepet", f"{sum(o.total_amount for o in self.orders) / max(len(self.orders), 1):.2f}₺"),
            ("Aktif Ürün", str(len(self.products)))
        ]
        
        kpi_width = 150
        for i, (kpi_name, kpi_value) in enumerate(kpis):
            kpi_rect = pygame.Rect(
                content_rect.x + 20 + i * (kpi_width + 20),
                kpi_y,
                kpi_width,
                80
            )
            
            pygame.draw.rect(self.screen, self.colors['accent_blue'], kpi_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], kpi_rect, 1)
            
            name_surface = self.fonts['small'].render(kpi_name, True, self.colors['white'])
            name_rect = name_surface.get_rect(centerx=kpi_rect.centerx, y=kpi_rect.y + 10)
            self.screen.blit(name_surface, name_rect)
            
            value_surface = self.fonts['large'].render(kpi_value, True, self.colors['white'])
            value_rect = value_surface.get_rect(center=(kpi_rect.centerx, kpi_rect.y + 50))
            self.screen.blit(value_surface, value_rect)
        
        # Simple chart placeholder
        chart_rect = pygame.Rect(content_rect.x + 20, kpi_y + 100, content_rect.width - 40, 200)
        pygame.draw.rect(self.screen, self.colors['medium_gray'], chart_rect)
        pygame.draw.rect(self.screen, self.colors['border_light'], chart_rect, 1)
        
        chart_text = self.fonts['medium'].render("Satış Grafiği (Geliştiriliyor)", True, self.colors['text_secondary'])
        chart_text_rect = chart_text.get_rect(center=chart_rect.center)
        self.screen.blit(chart_text, chart_text_rect)
    
    def draw_accounting_tab(self):
        """Draw accounting and ERP tab"""
        content_rect = pygame.Rect(
            self.panel_rect.x,
            self.panel_rect.y + self.tab_height,
            self.panel_rect.width,
            self.panel_rect.height - self.tab_height
        )
        
        self.draw_panel_background(content_rect, "dark")
        
        # Accounting header
        header_text = self.fonts['large'].render("Muhasebe & ERP", True, self.colors['text_primary'])
        self.screen.blit(header_text, (content_rect.x + 10, content_rect.y + 10))
        
        # Quick actions
        actions_y = content_rect.y + 50
        actions = [
            "Fatura Oluştur",
            "Gider Ekle",
            "Stok Raporu",
            "Vergi Beyanı",
            "Kasa Durumu",
            "Müşteri Listesi"
        ]
        
        action_width = 200
        action_height = 40
        
        for i, action in enumerate(actions):
            row = i // 3
            col = i % 3
            
            action_rect = pygame.Rect(
                content_rect.x + 20 + col * (action_width + 20),
                actions_y + row * (action_height + 10),
                action_width,
                action_height
            )
            
            pygame.draw.rect(self.screen, self.colors['primary_blue'], action_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], action_rect, 1)
            
            action_surface = self.fonts['medium'].render(action, True, self.colors['white'])
            action_text_rect = action_surface.get_rect(center=action_rect.center)
            self.screen.blit(action_surface, action_text_rect)
        
        # Financial summary
        summary_y = actions_y + 120
        summary_rect = pygame.Rect(content_rect.x + 20, summary_y, content_rect.width - 40, 150)
        pygame.draw.rect(self.screen, self.colors['medium_gray'], summary_rect)
        pygame.draw.rect(self.screen, self.colors['border_light'], summary_rect, 1)
        
        summary_title = self.fonts['medium'].render("Mali Durum Özeti", True, self.colors['text_primary'])
        self.screen.blit(summary_title, (summary_rect.x + 10, summary_rect.y + 10))
        
        # Financial data
        total_revenue = sum(o.total_amount for o in self.orders)
        financial_items = [
            f"Toplam Ciro: {total_revenue:.2f}₺",
            f"Bu Ay Satış: {sum(o.total_amount for o in self.orders if o.order_date.month == datetime.now().month):.2f}₺",
            f"Bekleyen Faturalar: {len([o for o in self.orders if o.status == OrderStatus.CONFIRMED])}",
            f"Toplam Ürün Değeri: {sum(p.price * p.stock for p in self.products):.2f}₺"
        ]
        
        for i, item in enumerate(financial_items):
            item_surface = self.fonts['small'].render(item, True, self.colors['text_primary'])
            self.screen.blit(item_surface, (summary_rect.x + 20, summary_rect.y + 40 + i * 25))
    
    def draw_notifications_tab(self):
        """Draw notifications tab"""
        content_rect = pygame.Rect(
            self.panel_rect.x,
            self.panel_rect.y + self.tab_height,
            self.panel_rect.width,
            self.panel_rect.height - self.tab_height
        )
        
        self.draw_panel_background(content_rect, "dark")
        
        # Notifications header
        header_text = self.fonts['large'].render("Bildirimler", True, self.colors['text_primary'])
        self.screen.blit(header_text, (content_rect.x + 10, content_rect.y + 10))
        
        # Clear all button
        clear_button_rect = pygame.Rect(content_rect.right - 120, content_rect.y + 10, 100, 30)
        pygame.draw.rect(self.screen, self.colors['red'], clear_button_rect)
        pygame.draw.rect(self.screen, self.colors['border_light'], clear_button_rect, 1)
        
        clear_text = self.fonts['small'].render("Tümünü Sil", True, self.colors['white'])
        clear_text_rect = clear_text.get_rect(center=clear_button_rect.center)
        self.screen.blit(clear_text, clear_text_rect)
        
        # Notifications list
        notif_y = content_rect.y + 50
        for i, notification in enumerate(self.notifications[:15]):  # Show first 15 notifications
            notif_rect = pygame.Rect(
                content_rect.x + 10,
                notif_y + i * 35,
                content_rect.width - 20,
                30
            )
            
            # Notification background
            if not notification.read:
                notif_bg_color = self.colors['accent_blue']
                text_color = self.colors['white']
            else:
                notif_bg_color = self.colors['light_gray']
                text_color = self.colors['text_primary']
            
            pygame.draw.rect(self.screen, notif_bg_color, notif_rect)
            pygame.draw.rect(self.screen, self.colors['border_light'], notif_rect, 1)
            
            # Notification content
            title_surface = self.fonts['small'].render(notification.title, True, text_color)
            self.screen.blit(title_surface, (notif_rect.x + 10, notif_rect.y + 5))
            
            time_text = notification.timestamp.strftime("%H:%M")
            time_surface = self.fonts['small'].render(time_text, True, text_color)
            time_rect = time_surface.get_rect(right=notif_rect.right - 10, y=notif_rect.y + 5)
            self.screen.blit(time_surface, time_rect)
    
    def get_status_color(self, status: OrderStatus):
        """Get color for order status"""
        status_colors = {
            OrderStatus.PENDING: self.colors['yellow'],
            OrderStatus.CONFIRMED: self.colors['orange'],
            OrderStatus.PREPARING: self.colors['blue'],
            OrderStatus.SHIPPED: self.colors['accent_blue'],
            OrderStatus.DELIVERED: self.colors['green'],
            OrderStatus.CANCELLED: self.colors['red']
        }
        return status_colors.get(status, self.colors['medium_gray'])
    
    def handle_click(self, pos):
        """Handle mouse clicks on trade panel"""
        if not self.panel_rect.collidepoint(pos):
            return False
        
        # Check tab clicks
        tab_rect = pygame.Rect(self.panel_rect.x, self.panel_rect.y, self.panel_rect.width, self.tab_height)
        if tab_rect.collidepoint(pos):
            tabs = ["orders", "products", "analytics", "accounting", "notifications"]
            tab_width = self.panel_rect.width // len(tabs)
            clicked_tab = (pos[0] - self.panel_rect.x) // tab_width
            
            if 0 <= clicked_tab < len(tabs):
                self.current_tab = tabs[clicked_tab]
                if self.current_tab == "notifications":
                    self.notification_count = 0  # Reset notification count
                return True
        
        # Check order clicks in orders tab
        if self.current_tab == "orders":
            order_list_rect = pygame.Rect(self.panel_rect.x + 10, self.panel_rect.y + self.tab_height + 10, 400, self.panel_rect.height - self.tab_height - 20)
            if order_list_rect.collidepoint(pos):
                relative_y = pos[1] - (order_list_rect.y + 50)
                order_index = relative_y // 50
                
                if 0 <= order_index < len(self.orders):
                    self.selected_order = self.orders[order_index]
                    return True
        
        return False
    
    def draw(self):
        """Draw the complete trade panel"""
        # Main panel background
        self.draw_panel_background(self.panel_rect, "primary")
        
        # Draw tabs
        self.draw_tabs()
        
        # Draw current tab content
        if self.current_tab == "orders":
            self.draw_orders_tab()
        elif self.current_tab == "products":
            self.draw_products_tab()
        elif self.current_tab == "analytics":
            self.draw_analytics_tab()
        elif self.current_tab == "accounting":
            self.draw_accounting_tab()
        elif self.current_tab == "notifications":
            self.draw_notifications_tab()

# Example usage in main interface
def integrate_trade_panel(main_interface):
    """Integrate trade panel into main interface"""
    trade_panel = TradePanel(
        main_interface.screen,
        main_interface.fonts,
        main_interface.colors
    )
    
    # Add to main interface
    main_interface.trade_panel = trade_panel
    
    # Add keyboard shortcut
    def handle_trade_key():
        main_interface.show_trade_panel = not getattr(main_interface, 'show_trade_panel', False)
    
    # Add to event handling
    def enhanced_event_handler(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                handle_trade_key()
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if getattr(main_interface, 'show_trade_panel', False):
                return trade_panel.handle_click(event.pos)
        return False
    
    return enhanced_event_handler

if __name__ == "__main__":
    print("Birlikteyiz Trade Panel - E-commerce Integration")
    print("Features:")
    print("- Real-time order management")
    print("- Multi-marketplace integration")
    print("- Gamified ERP system")
    print("- Responsive design")
    print("- Live notifications")

